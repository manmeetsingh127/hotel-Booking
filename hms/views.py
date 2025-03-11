from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponse
from .models import Account, Hotel, Room, Reservation, Waitlist
from django.core.files.storage import FileSystemStorage
import math

def home(request):

    homeContext = {
        "title": "Home",
        "login_success": False,
        "hotels": Hotel.objects.all(),
        "notFound": False,
        "isEmployee":False
    }

    if request.session.get('login_email'):
        homeContext['login_success'] = True
        loginEmail = request.session.get('login_email')
        accType = Account.objects.filter(email=loginEmail).first().accountType
        if accType == 'employee':
            homeContext['isEmployee'] = True
    if request.method == 'GET':
        if request.GET.get('search'):
            if Hotel.objects.filter(name__contains=request.GET['search']):
                homeContext['hotels'] = Hotel.objects.filter(name__contains=request.GET['search'])
            else:
                homeContext['notFound'] = True


    return render(request, 'hms/home.html', homeContext)


def login(request):
    if request.method == 'POST':
        if request.POST:
            data = request.POST
            email = data['email']
            password = data['password']
            accountSearch = Account.objects.filter(email=email, password=password)
            if accountSearch:
                request.session['login_email'] = email
                print('logged in with', email)
                return redirect("/success?msg=login")

    return render(request, 'hms/login.html', {'title': "Login"})


def logout(request):
    try:
        del request.session['login_email']
        print('logged out')
    except KeyError:
        print('logout error')
        pass

    return redirect("/")

def account(request):
    accountContext = {
        'title': "account",
        'login_success':True,
        'isEmployee':True,
        'accounts': Account.objects.all(),
        'hotels': Hotel.objects.all(),
        "rooms": Room.objects.all(),
        'reservations':Reservation.objects.all(),
        'waitlist':Waitlist.objects.all(),
    }
    if request.session.get('login_email'):
        loggedEmail = request.session.get('login_email')
        accType = Account.objects.filter(email=loggedEmail).first().accountType
        if accType == 'employee':

            if request.method == 'POST':
                hotelName = request.POST['hotelName']
                hotelAddress = request.POST['hotelAddress']
                hotelDesc = request.POST['hotelDesc']
                hotelImage = request.FILES.get('image', None)
                if hotelName and hotelDesc and hotelAddress and hotelImage:
                    fs = FileSystemStorage()
                    imageName = fs.save(hotelName + hotelDesc[2:6] + hotelImage.name, hotelImage)
                    hotels = Hotel.objects.create(name=hotelName, address=hotelAddress, desc=hotelDesc, image=imageName)
                else:
                    return HttpResponse("<script>return alert(\'complete all fields\');</script>"
                                       "<meta http-equiv=\"refresh\" content=\"0.5; URL=/account\" />")
            if request.method == 'GET':
                roomType = request.GET.get('roomType', None)
                roomHotelId = request.GET.get('hotel', None)
                roomPrice = request.GET.get('price', None)
                roomCount = request.GET.get('count', None)
                checkoutCustomer = request.GET.get('checkoutId', None)
                waitlistId = request.GET.get('waitlistConfirm', None)

                if roomType and roomPrice and roomCount and roomHotelId:
                    Room.objects.create(roomType=roomType.upper(), hotelId=roomHotelId, price=roomPrice, available=roomCount)
                    return redirect('/account')
                if checkoutCustomer:
                    reservationQuery = Reservation.objects.filter(accountId=checkoutCustomer)
                    roomQuery = Room.objects.filter(roomId=reservationQuery.first().roomId)
                    oldRoomCount = roomQuery.first().available
                    roomQuery.update(available=oldRoomCount+1)
                    reservationQuery.first().delete()
                    return redirect('/account')
                if waitlistId:
                    waitlistQuery = Waitlist.objects.filter(waitlistId=waitlistId)
                    roomQuery = Room.objects.filter(roomId=waitlistQuery.first().roomId)
                    if roomQuery.first().available <= 0:
                        return HttpResponse('<center><h1>Error:no enough rooms to confirm <br>Please Try Again</h1></center>'
                                            '<meta http-equiv="refresh" content="2; URL=/account\" />')
                    else:
                        waitlistQuery.update(status='confirmed')
                        Reservation.objects.create(hotelId=waitlistQuery.first().hotelId,
                                           hotelName=Hotel.objects.filter(hotelId=waitlistQuery.first().hotelId).first().name,
                                           customerName=waitlistQuery.first().customerName,
                                           roomId=waitlistQuery.first().roomId,
                                           accountId=waitlistQuery.first().accountId,
                                           date=waitlistQuery.first().date)
                        roomQuery = Room.objects.filter(roomId=waitlistQuery.first().roomId)
                        oldRoomCount = roomQuery.first().available
                        roomQuery.update(available=oldRoomCount - 1)
                    return redirect('/account')

        else:
            return redirect("/")

    else:
        return redirect("/")
    return render(request, 'hms/account.html', accountContext)


def signup(request):
    if request.session.get('login_email'):
        return redirect("/login")
    if request.method == 'POST':
        if request.POST:
            data = request.POST
            email = data['email'].lower()
            firstName = data['first']
            lastName = data['last']
            password = data['password']
            accType = data['accType']
            if accType == 'employee':
                salary = 0
            else:
                salary = None
            if Account.objects.filter(email=email):
                return HttpResponse('<center><h1>email is already registered<br>Please Try another one</h1></center>'
                                    '<meta http-equiv="refresh" content="1.5; URL=/signup\" />')
            newAcc = Account.objects.create(
                email=email,
                password=password,
                firstName=firstName,
                lastName=lastName,
                accountType=accType,
                salary=salary)
            Account.save(newAcc)
            return redirect('/login')

    return render(request, 'hms/signup.html', {'title': "Signup"})

def delete(request):
    if request.method == 'GET' and request.session.get('login_email'):
        if request.GET['id']:
            theAccount = Account.objects.filter(accountId=request.GET['id'])
            if theAccount is None:
                return HttpResponse('<center><h1>Error:Unvalid account!<br>Please Try Again</h1></center>'
                                    '<meta http-equiv="refresh" content="1.5; URL=/account\" />')
            else:
                theAccount.delete()
    else:
        return redirect("/login")
    return redirect("/account")

def edit(request):
    editContext = {
        'theAccount':None
    }
    if request.method == 'GET':
        if request.GET['id']:
            theAccount = Account.objects.filter(accountId=request.GET['id']).first()
            if theAccount is None:
                return HttpResponse('<center><h1>Error:Unvalid account!<br>Please Try Again</h1></center>'
                                    '<meta http-equiv="refresh" content="1.5; URL=/account\" />')
            else:
                editContext['theAccount'] = theAccount

    if request.method == 'POST':
        accountId = request.GET
        updateData = request.POST
        Account.objects.filter(accountId=accountId['id']).update(
                email=updateData['email'],
                password=updateData['password'],
                firstName=updateData['firstName'],
                lastName=updateData['lastName'],
                accountType=updateData['accType'],
                rewardPoints=updateData.get('rewardPoints', 0),
                salary=updateData.get('salary'),
            )
        return redirect("/success?msg=accountEdit")



    return render(request, 'hms/edit.html', editContext)

def success(request):
    successMsg = {
        'msg':None
    }
    if request.method == 'GET':
        if request.GET.get("msg") == 'login':
            successMsg['msg'] = 'login'
        elif request.GET.get("msg") == 'accountEdit':
            successMsg['msg'] = 'accountEdit'
    return render(request, 'hms/success.html', successMsg)

def hotel(request):
    hotelContext = {
        'hotel':None,
        'rooms':None,
        'login_success': True,
    }
    if not request.session.get('login_email'):
        return redirect('/login')
    if request.method == 'GET':
        hotelId = request.GET.get('id', None)
        rooms = Room.objects.filter(hotelId=hotelId)
        if hotelId:
            if Hotel.objects.filter(hotelId=hotelId):
                hotelContext['hotel'] = Hotel.objects.filter(hotelId=hotelId).first()
                if rooms:
                    hotelContext['rooms'] = rooms
            else:
                return redirect('/')
        else:
            return redirect('/')
    if request.method == 'POST':

        if request.POST.get('selectedRoom', None) and request.POST.get('selectedDate', None):
            bookingEmail = request.session.get('login_email')
            customer = Account.objects.filter(email=bookingEmail).first()
            customerQuery = Account.objects.filter(email=bookingEmail)
            bookingRoom = Room.objects.filter(roomId=request.POST.get('selectedRoom')).first()
            bookingRoomQuery = Room.objects.filter(roomId=request.POST.get('selectedRoom'))
            bookingHotel = Hotel.objects.filter(hotelId=bookingRoom.hotelId).first()

            roomCountBefore = bookingRoom.available
            if roomCountBefore > 0:
                reservation = Reservation.objects.create(hotelId=bookingHotel.hotelId, hotelName=bookingHotel.name, customerName=customer.firstName,roomId=bookingRoom.roomId,
                                                         accountId=customer.accountId, date=str(request.POST.get('selectedDate')))
                bookingRoomQuery.update(available=roomCountBefore-1)
                calculatedRP = math.ceil(0.02 * bookingRoom.price)
                oldRewardCount = customer.rewardPoints
                customerQuery.update(rewardPoints=calculatedRP+oldRewardCount)
                bookingContext = {
                    'login_success':True,
                    'isEmployee':False,
                    'bookedHotel':bookingHotel.name,
                    'roomNum':bookingRoom.roomId,
                    'customerName': customer.firstName,
                    'bookingPrice': bookingRoom.price,
                    'customerEmail':bookingEmail,
                    'earnedPoints': calculatedRP,
                    'bookedDate':str(request.POST.get('selectedDate'))
                }
                loginEmail = request.session.get('login_email')
                accType = Account.objects.filter(email=loginEmail).first().accountType
                if accType == 'employee':
                    bookingContext['isEmployee'] = True

                return render(request, 'hms/booking.html', bookingContext)
            else:
                Waitlist.objects.create(customerName=customer.firstName,hotelId=bookingHotel.hotelId, roomId=bookingRoom.roomId, accountId=customer.accountId,
                                        date=str(request.POST.get('selectedDate')))
                return HttpResponse("there are no rooms left we registered you in the waitlist")


        else:
            return HttpResponse("<meta http-equiv=\"refresh\" content=\"0\">"
                                "<script>alert(\"Please Choose a Room\");</script>")

    return render(request, 'hms/hotel.html', hotelContext)

def booking(request):
    if not request.session.get('login_email'):
        return redirect('/login')

    return render(request, 'hms/booking.html', {})

def myBooking(request):
    myBookingContext = {
        'login_success': True,
        'isEmployee':False,
        'bookings': None,
        'waitlist':None
    }
    if request.session.get('login_email'):
        loginEmail = request.session.get('login_email')
        accType = Account.objects.filter(email=loginEmail).first().accountType
        if accType == 'employee':
            myBookingContext['isEmployee'] = True

        accountId = Account.objects.filter(email=loginEmail).first().accountId
        bookings = Reservation.objects.filter(accountId=accountId)
        waitlist = Waitlist.objects.filter(accountId=accountId).order_by('-date')
        myBookingContext['bookings'] = bookings
        myBookingContext['waitlist'] = waitlist
    else:
        return redirect('/login')
    return render(request, 'hms/myBooking.html', myBookingContext)

def profile(request):
    profileContext = {
        'login_success': True,
        'isEmployee': False,
        'userAccount':None
    }

    if request.session.get('login_email'):
        loginEmail = request.session.get('login_email')
        accType = Account.objects.filter(email=loginEmail).first().accountType
        if accType == 'customer':
            userAccount = Account.objects.filter(email=loginEmail)
            if userAccount:
                profileContext['userAccount'] = userAccount.first()
            else:
                return redirect('/login')
        else:
            return redirect('/account')
        if request.method == 'POST':
            if request.POST:
                newData = request.POST
                if newData['email'] and newData['first'] and newData['last'] and newData['password']:
                    userAccount.update(email=newData['email'], firstName=newData['first'], lastName=newData['last'], password=newData['password'])
                    del request.session['login_email']
                    return redirect('/login')
                else:
                    return HttpResponse('<meta http-equiv=\"refresh\" content=\"0\">'
                                        '<script>alert(\"fill all the fields\");</script>')

    else:
        return redirect('/login')

    return render(request, 'hms/profile.html', profileContext)
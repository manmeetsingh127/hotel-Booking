from django.contrib import admin
from .models import Hotel, Room, Account, Reservation, Waitlist


admin.site.register(Hotel)
admin.site.register(Room)
admin.site.register(Account)
admin.site.register(Reservation)
admin.site.register(Waitlist)

# from django.db.models.signals import pre_save
# from django.dispatch import receiver
# from django.utils.timezone import now
# from .models import UpcomingEvent, MREvents

# @receiver(pre_save, sender=UpcomingEvent)
# def transition_to_mrevents(sender, instance, **kwargs):
#     if instance.date == now().date() and instance.approved:
#         # Create a new MREvents entry
#         MREvents.objects.create(
#             title=instance.title,
#             description=instance.description,
#             date=instance.date,
#             time=instance.time,
#             venue=instance.venue,
#             contact_number=instance.contact_number,
#             email=instance.email,
#             link=instance.link,
#             image=instance.image,
#             category=instance.category,
#             approved=True,  # Preserve approval
#             status='ongoing'
#         )
#         instance.status = 'ongoing'  # Update status
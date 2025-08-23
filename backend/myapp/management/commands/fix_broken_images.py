from django.core.management.base import BaseCommand
from myapp.models import CustomUser
import os

class Command(BaseCommand):
    help = 'Fix broken profile image references'

    def handle(self, *args, **options):
        users_with_broken_images = []
        
        for user in CustomUser.objects.exclude(profile_image=''):
            if user.profile_image and hasattr(user.profile_image, 'path'):
                if not os.path.exists(user.profile_image.path):
                    self.stdout.write(
                        self.style.WARNING(f'Broken image reference for user {user.username}: {user.profile_image.path}')
                    )
                    # Clear the broken reference
                    user.profile_image = None
                    user.save()
                    users_with_broken_images.append(user.username)
        
        if users_with_broken_images:
            self.stdout.write(
                self.style.SUCCESS(f'Fixed broken image references for {len(users_with_broken_images)} users: {", ".join(users_with_broken_images)}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('No broken image references found.')
            )

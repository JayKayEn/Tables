from django.db import models
from django.contrib.auth import models as auth_models
from django.utils import timezone
from time import strftime, gmtime
from instagram.client import InstagramAPI
from .keys import client_info

client_id = client_info['client_id']
client_secret = client_info['client_secret']

class AccessToken(models.Model):
    user = models.OneToOneField('auth.User')
    value = models.TextField()

# class Media(models.Model):
#     url = models.URLField()
#     like_count = model.PositiveIntegerField(default=0)
#     caption = models.TextField(blank=True, null=True)

# Store IG user data and then also tags and notes
class Person(models.Model):
    profile = models.CharField(max_length=30, null=True, unique=True)
    user_id = models.CharField(max_length=20, primary_key=True)
    username = models.CharField(max_length=30)
    profile_picture_url = models.URLField(null=True)
    full_name = models.CharField(max_length=20, blank=True, null=True)
    # profile_picture_img = models.ImageField()
    # website = models.URLField(null=True, blank=True)
    # bio = models.TextField(blank=True, null=True)
    # tags = TaggableManager()
    # notes = models.TextField(blank=True, null=True)
    # recent_media = models.ManyToManyField()
    most_recent_post = models.CharField(max_length=10, null=True)
    needs_review = models.BooleanField(default=False)
    new_post_count = models.PositiveIntegerField(default=0)

    @staticmethod
    def get_or_create_person(user_id, username, full_name, profile_picture_url):
        try:
            person = Person.objects.get(user_id=user_id)
            person.username = username
            person.profile_picture_url = profile_picture_url
            # person.website = website
            # person.bio = bio
            person.full_name = full_name
            # person.save(update_fields=['username', 'website', 'profile_picture_url', 'full_name', 'bio'])
            person.save(update_fields=['username', 'profile_picture_url', 'full_name'])
        except Person.DoesNotExist:
            person = Person.objects.create(
                user_id = user_id,
                username = username,
                profile_picture_url = profile_picture_url,
                # website = website,
                # bio = bio,
                full_name = full_name
            )
        return person

    def update(self, access_token):
        api = InstagramAPI(access_token=access_token, client_secret=client_secret)
        recent_media, next_ = api.user_recent_media(user_id=self.user_id, count=100)
        num = len(recent_media)
        while next_ and num < 100:
            more_recent_media, next_ = api.user_recent_media(with_next_url=next_)
            recent_media.extend(more_recent_media)
            num = len(recent_media)


    def update_profile_picture(self, url):
        import requests
        from django.core.files import File
        from django.core.files.temp import NamedTemporaryFile
        req = requests.get(url)
        img = NamedTemporaryFile(delete=True)
        img.write(req.content)
        img.flush()
        self.profile_picture_img.save("%s.jpg" % (self.username), File(img), save=True)

    class Meta:
        ordering = ['username']

class Table(models.Model):
    user = models.ForeignKey('auth.User')
    name = models.CharField(max_length=128)
    people = models.ManyToManyField(Person)
    needs_review = models.BooleanField(default=False)
    # tags = TaggableManager()
    # notes = models.TextField(blank=True, null=True)

    def update(self):
        access_token = AccessToken.objects.get(user=self.user)
        for person in self.people.all():
            person.update(access_token)

    class Meta:
        unique_together = ('user', 'name',)

    # def update(self, user):
    #     tables = Table.objects.filter(user=user)
    #     for table in tables:
    #         people = table.people
    #         for person in people:

# Persons that follow the user
# class Followers(models.Model):
#     user = models.ForeignKey('auth.User')
#     people = models.ManyToManyField(Person)
#     last_updated = models.DateTimeField(default=timezone.now)

# Persons that the user follows
class Followees(models.Model):
    user = models.OneToOneField('auth.User')
    people = models.ManyToManyField(Person)
    last_updated = models.DateTimeField(default=timezone.now)

    def update(self, api):
        person = Person.objects.get(profile=self.user.get_username())
        user_id = person.user_id

        self.people.clear()
        self.save()

        people, next_ = api.user_follows(user_id=user_id, count=100)
        while next_:
            more_people, next_ = api.user_follows(with_next_url=next_)
            people.extend(more_people)

        for person in people:
            user_id = person.id
            username = person.username
            profile_picture_url = person.profile_picture
            full_name = person.full_name.strip()
            # website = person.website
            # bio = person.bio
            person = Person.get_or_create_person(user_id, username, full_name, profile_picture_url)
            self.people.add(person)
        self.save()

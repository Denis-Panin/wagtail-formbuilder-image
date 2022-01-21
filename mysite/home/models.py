import json
from os.path import splitext
from typing import Collection

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from wagtail.images import get_image_model
from wagtail.images.fields import WagtailImageField
from wagtail.tests.testapp.views import CustomSubmissionsImageView
from wagtail.core.models import Collection

from django.db import models

from wagtail.core.models import Page

# import for FORM
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel, FieldRowPanel,
    InlinePanel, MultiFieldPanel
)
from wagtail.core.fields import RichTextField
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField, AbstractFormSubmission, \
    FORM_FIELD_CHOICES, AbstractForm


class FormField(AbstractFormField):
    # Todo me ------------------
    field_type = models.CharField(
        verbose_name='field type',
        max_length=16,
        choices=list(FORM_FIELD_CHOICES) + [('image', 'Upload Image')]
    )
    # Todo me ------------------
    page = ParentalKey('FormPage', on_delete=models.CASCADE, related_name='form_fields')


class FormPage(AbstractEmailForm):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)
    # Todo me ----------------
    uploaded_image_collection = models.ForeignKey(
        'wagtailcore.Collection',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    submissions_list_view_class = CustomSubmissionsImageView

    # Todo me -----------------

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('intro', classname="full"),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('thank_you_text', classname="full"),
        # MultiFieldPanel([
        #     FieldRowPanel([
        #         FieldPanel('from_address', classname="col6"),
        #         FieldPanel('to_address', classname="col6"),
        #     ]),
        #     FieldPanel('subject'),
        # ], "Email"),
    ]

    # Todo me -----------------
    settings_panels = AbstractForm.settings_panels + [
        FieldPanel('uploaded_image_collection')
    ]

    def get_uploaded_image_collection(self):
        """
        Returns a Wagtail Collection, using this form's saved value if present,
        otherwise returns the 'Root' Collection.
        """
        collection = self.uploaded_image_collection
        return collection or Collection.get_first_root_node()

    # Todo me -----------------

    @staticmethod
    def get_image_title(filename):
        """
        Generates a usable title from the filename of an image upload.
        Note: The filename will be provided as a 'path/to/file.jpg'
        """

        if filename:
            result = splitext(filename)[0]
            result = result.replace('-', ' ').replace('_', ' ')
            return result.title()
        return ''

    def process_form_submission(self, form):
        """
        Processes the form submission, if an Image upload is found, pull out the
        files data, create an actual Wgtail Image and reference its ID only in the
        stored form response.
        """

        cleaned_data = form.cleaned_data

        for name, field in form.fields.items():
            if isinstance(field, WagtailImageField):
                image_file_data = cleaned_data[name]
                if image_file_data:
                    ImageModel = get_image_model()

                    kwargs = {
                        'file': cleaned_data[name],
                        'title': self.get_image_title(cleaned_data[name].name),
                        'collection': self.get_uploaded_image_collection(),
                    }

                    if form.user and not form.user.is_anonymous:
                        kwargs['uploaded_by_user'] = form.user

                    image = ImageModel(**kwargs)
                    image.save()
                    # saving the image id
                    # alternatively we can store a path to the image via image.get_rendition
                    cleaned_data.update({name: image.pk})
                else:
                    # remove the value from the data
                    del cleaned_data[name]

        submission = self.get_submission_class().objects.create(
            form_data=json.dumps(form.cleaned_data, cls=DjangoJSONEncoder),
            page=self,
        )

        # important: if extending AbstractEmailForm, email logic must be re-added here
        # if self.to_address:
        #    self.send_mail(form)

        return submission

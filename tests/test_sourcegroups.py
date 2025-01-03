import pytest
from django.core.files import File

from imagekit.signals import source_saved

from .models import AbstractImageModel, ConcreteImageModel, ImageModel, Photo
from .utils import get_image_file


def make_logging_receiver():
    logs = []

    def receiver(sender, signal, source):
        # image_field is the name of the source field.
        logs.append((sender.image_field, sender.model_class))

    return receiver, logs


@pytest.mark.django_db(transaction=True)
def test_source_saved_signal():
    """
    Creating a new instance with an image causes the source_saved signal to be
    dispatched.

    """
    receiver, logs = make_logging_receiver()
    source_saved.connect(receiver)
    with File(get_image_file(), name='reference.png') as image:
        Photo.objects.create(original_image=image)
    assert logs == [('original_image', Photo), ('original_image', Photo),
                    ('thumbnail', Photo)]


@pytest.mark.django_db(transaction=True)
def test_no_source_saved_signal():
    """
    Creating a new instance without an image shouldn't cause the source_saved
    signal to be dispatched.

    https://github.com/matthewwithanm/django-imagekit/issues/214

    """
    receiver, logs = make_logging_receiver()
    source_saved.connect(receiver)
    ImageModel.objects.create()
    assert logs == []


@pytest.mark.django_db(transaction=True)
def test_abstract_model_signals():
    """
    Source groups created for abstract models must cause signals to be
    dispatched on their concrete subclasses.

    """
    receiver, logs = make_logging_receiver()
    source_saved.connect(receiver)
    with File(get_image_file(), name='reference.png') as image:
        ConcreteImageModel.objects.create(original_image=image)
    assert logs == [('original_image', AbstractImageModel)]

import copy

from .errors import ConfigError
from .serializers import yaml_serializer


class Config(object):
    def __init__(self):
        self.url = None
        self.base_dir = None
        self.downloads_dir = None
        self.images_dir = None
        self.source_ext = None
        self.pages = list()

    def __eq__(self, other):
        first = copy.copy(self.__dict__)
        del first['pages']

        second = copy.copy(other.__dict__)
        del second['pages']

        if len(self.pages) != len(other.pages):
            return False

        for first_page, second_page in zip(self.pages, other.pages):
            if not (first_page == second_page):
                return False

        return first == second


class PageConfig(object):
    def __init__(self):
        self.id = None
        self.parent_id = None

        self.title = None
        self.source = None
        self.link = None
        self.watermark = None

        self.images = list()
        self.downloads = list()

        self.pages = list()

    def __eq__(self, other):
        first = copy.copy(self.__dict__)
        del first['images']
        del first['downloads']

        second = copy.copy(other.__dict__)
        del second['images']
        del second['downloads']

        if len(self.images) != len(other.images):
            return False

        if len(self.downloads) != len(other.downloads):
            return False

        for first_attach, second_attach in zip(self.images, other.images):
            if not (first_attach == second_attach):
                return False

        for first_attach, second_attach in zip(self.downloads, other.downloads):
            if not (first_attach == second_attach):
                return False

        return first == second


class PageAattachmentConfig(object):
    TYPE_ATTACHMENT = 'attachment'
    TYPE_IMAGE = 'image'

    def __init__(self):
        self.type = self.TYPE_ATTACHMENT
        self.path = None

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class PageImageAattachmentConfig(PageAattachmentConfig):
    def __init__(self):
        self.type = self.TYPE_IMAGE
        super(PageImageAattachmentConfig, self).__init__()


class ConfigLoader:

    @classmethod
    def from_yaml(cls, config_path):
        with open(config_path, 'rb') as f:
            config = yaml_serializer.load(f)
        return cls.from_dict(config)

    @classmethod
    def from_dict(cls, config_dict):
        if 'version' not in config_dict:
            raise ConfigError('`version` param is required')

        if config_dict['version'] != 2:
            raise ConfigError('invalid config version. required: 2')

        config = Config()

        for attr in ('url', 'base_dir', 'downloads_dir', 'images_dir', 'source_ext'):
            if attr in config_dict:
                setattr(config, attr, config_dict[attr])

        config.pages = cls._pages_from_list(config_dict.get('pages', list()))

        return config

    @classmethod
    def _pages_from_list(cls, pages_list):
        pages = list()
        for page_dict in pages_list:
            pages.append(cls._page_from_dict(page_dict))
        return pages

    @classmethod
    def _page_from_dict(cls, page_dict):
        page_config = PageConfig()

        for attr in ('parent_id', 'title', 'source', 'link', 'watermark'):
            if attr in page_dict:
                setattr(page_config, attr, page_dict[attr])

        if 'attachments' in page_dict:
            for path in page_dict['attachments'].get('images', list()):
                page_config.images.append(cls._attach_from_path(path, PageImageAattachmentConfig))
            for path in page_dict['attachments'].get('downloads', list()):
                page_config.downloads.append(cls._attach_from_path(path, PageAattachmentConfig))

        page_config.pages = cls._pages_from_list(page_dict.get('pages', list()))

        return page_config

    @staticmethod
    def _attach_from_path(attach_path, attach_class):
        attach = attach_class()
        attach.path = attach_path
        return attach


def flatten_page_config_list(pages):
    for page in pages:
        yield page
        for subpage in flatten_page_config_list(page.pages):
            yield subpage

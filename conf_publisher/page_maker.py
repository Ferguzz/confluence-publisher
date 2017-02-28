from . import log
from .confluence import Page, Ancestor
from .errors import ConfigError


def setup_config_overrides(config, url=None):
    if url:
        config.url = url


def empty_page(space_key, title, ancestor_id, ancestor_type):
    ancestor = Ancestor()
    ancestor.id = ancestor_id
    ancestor.type = ancestor_type

    page = Page()
    page.space_key = space_key
    page.title = title
    page.body = ''
    page.ancestors.append(ancestor)

    return page


def make_page(parent_page, title, page_manager):
    page = empty_page(parent_page.space_key, title, parent_page.id, parent_page.type)
    page_id = page_manager.exists(page)
    if not page_id:
        page_id = page_manager.create(page)
        log.info('Page with id {page_id} has been created. Parent page id: {parent_id}'
                 .format(page_id=page_id, parent_id=parent_page.id))
    else:
        log.info('Page with id {page_id} already exists, no need to create it.'.format(page_id=page_id))
    return int(page_id)


def make_pages(validate_only, config, page_manager, parent_id=None):
    parent_page = None
    if parent_id and not validate_only:
        parent_page = page_manager.load(parent_id)

    for page_config in config.pages:
        cur_parent_id = parent_id or page_config.parent_id
        if not cur_parent_id:
            message = 'Page without parent page. Skip. Page title: {page_title}'.format(page_title=page_config.title)
            if validate_only:
                raise ConfigError(message)
            log.warning(message)
        elif not page_config.title:
            message = 'Page without title. Skip. Parent page id: {cur_parent_id}.'.format(cur_parent_id=cur_parent_id)
            if validate_only:
                raise ConfigError(message)
            log.warning(message)
        else:
            # Don't create any pages if we are only validating.
            if validate_only:
                page_config.id = 123
            else:
                cur_parent_page = parent_page or page_manager.load(cur_parent_id)
                page_config.id = make_page(cur_parent_page, page_config.title, page_manager)

        if len(page_config.pages):
            make_pages(validate_only, page_config, page_manager, page_config.id)

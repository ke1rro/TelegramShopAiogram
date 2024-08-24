import os


def delete_photo(photo_id):
    if os.path.isfile(f'app/bot_imgs/{photo_id}.jpg') and photo_id != 'Shop.jpg':
        os.remove(f'app/bot_imgs/{photo_id}.jpg')
        return True
    return True

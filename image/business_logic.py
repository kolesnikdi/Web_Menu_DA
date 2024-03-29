def user_directory_path(instance, filename):
    """
    Path to upload image for different apps request.
    Import inside to improve a circular import
    or putt function in to the model.Image
    :param instance:
    :type instance: image.models.Image
    :param filename:
    :type filename: str
    :return:
    """
    from image.models import Image
    if hasattr(instance, 'company_logo'):
        purpose = 'company_logo'
        company_id = instance.company_logo.id
    elif hasattr(instance, 'location_logo'):
        purpose = 'location_logo'
        company_id = instance.location_logo.company.id
    elif hasattr(instance, 'product_logo'):
        purpose = 'product_logo'
        company_id = instance.product_logo.company.id
    if hasattr(instance, 'id'):     # for update. If id exist we left current id
        img_id = instance.id
    else:
        last_img = Image.objects.last()
        img_id = last_img.id + 1 if last_img else 1
    result = 'company_{company_id}/{purpose}/{instance_id}_{filename}'.format(
        company_id=company_id,
        purpose=purpose,
        instance_id=img_id,
        filename=filename,
    )
    return result

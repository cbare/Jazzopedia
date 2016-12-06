import re, unidecode


def slugify(s):
    slug = unidecode.unidecode(s)
    slug = slug.encode('ascii', 'ignore').decode('ascii').lower()
    for c in ["'", '"']:
        slug = re.sub(c, '', slug)
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    return re.sub(r'--+',r'-',slug)

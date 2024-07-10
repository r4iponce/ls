"""Function used by >1 file."""

from ls import get_db


def verify_link_exist(url: str) -> bool:
    """
    Verify if an url already exist in database
    :param url: redirect source url
    :return: Bool, true if existed, else false.
    """
    db = get_db()
    query = db.execute("SELECT EXISTS(SELECT * FROM link  WHERE url=?)", (url,))
    result = query.fetchall()
    return result[0][0] == 1

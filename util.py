def get_domain(url):
  return ".".join(url.split("/")[2].split(".")[1:])
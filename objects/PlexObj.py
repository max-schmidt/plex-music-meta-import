class PlexObj:
	def __init__(self, plex_username, plex_password, plex_servername, plex_libraryname):
		self.plex_username = plex_username
		self.plex_password = plex_password
		self.plex_servername = plex_servername
		self.plex_libraryname = plex_libraryname
		self.plex_connection = 0

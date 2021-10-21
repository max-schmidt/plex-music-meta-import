from objects.MusicObj import MusicObj
class AlbumObj(MusicObj):
	def __init__(self, uid, plex_artist, plex_album, plex_year, plex_text, search_result_1, search_result_2, custom_url, apple_artist_1, apple_artist_2, apple_album_1, apple_album_2, apple_release_date_1, apple_release_date_2, apple_text, select_result, own_text, text_date, search_date, ignore):
		super().__init__(uid, plex_artist, plex_text, search_result_1, search_result_2, custom_url, select_result, apple_artist_1, apple_artist_2, apple_text, own_text, text_date, search_date, ignore)
		self.plex_album = plex_album
		self.plex_year = plex_year
		self.apple_album_1 = apple_album_1
		self.apple_album_2 = apple_album_2
		self.apple_release_date_1 = apple_release_date_1
		self.apple_release_date_2 = apple_release_date_2

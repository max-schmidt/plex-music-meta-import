from objects.MusicObj import MusicObj
class ArtistObj(MusicObj):
	def __init__(self, uid, plex_artist, plex_text, search_result_1, search_result_2, custom_url, apple_artist_1, apple_artist_2, apple_text, select_result, lastfm_artist, lastfm_text, wiki_text, own_text, text_date, apple_image, lastfm_image, pushed_poster, apple_image_changed, ignore_wiki, search_date, ignore):
		super().__init__(uid, plex_artist, plex_text, search_result_1, search_result_2, custom_url, select_result, apple_artist_1, apple_artist_2, apple_text, own_text, text_date, search_date, ignore)
		self.lastfm_artist = lastfm_artist
		self.lastfm_text = lastfm_text
		self.wiki_text = wiki_text
		self.apple_image = apple_image
		self.lastfm_image = lastfm_image
		self.pushed_poster = pushed_poster
		self.apple_image_changed = apple_image_changed
		self.ignore_wiki = ignore_wiki

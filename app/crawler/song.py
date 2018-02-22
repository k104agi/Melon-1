import requests
from bs4 import BeautifulSoup, NavigableString

__all__ = (
    'SongData',
)


class SongData:
    def __init__(self, song_id, title='', artist='', album=''):
        self.song_id = song_id
        self.title = title
        self.artist = artist
        self.album = album

        self._release_date = None
        self._lyrics = None
        self._genre = None
        self._producers = None

    def __str__(self):
        return f'{self.title} (아티스트: {self.artist}, 앨범: {self.album})'

    def get_detail(self):
        """
        자신의 _release_date, _lyrics, _genre, _producers를 채운다
        :return:
        """
        url = f'https://www.melon.com/song/detail.htm'
        params = {
            'songId': self.song_id,
        }
        response = requests.get(url, params)
        source = response.text
        soup = BeautifulSoup(source, 'lxml')
        # div.song_name의 자식 strong요소의 바로 다음 형제요소의 값을 양쪽 여백을 모두 잘라낸다
        # 아래의 HTML과 같은 구조
        # <div class="song_name">
        #   <strong>곡명</strong>
        #
        #              Heart Shaker
        # </div>
        div_entry = soup.find('div', class_='entry')
        title = div_entry.find('div', class_='song_name').strong.next_sibling.strip()
        artist = div_entry.find('div', class_='artist').get_text(strip=True)
        # 앨범, 발매일, 장르...에 대한 Description list
        dl = div_entry.find('div', class_='meta').find('dl')
        # isinstance(인스턴스, 클래스(타입))
        # items = ['앨범', '앨범명', '발매일', '발매일값', '장르', '장르값']
        items = [item.get_text(strip=True) for item in dl.contents if not isinstance(item, str)]
        it = iter(items)
        description_dict = dict(zip(it, it))

        album = description_dict.get('앨범')
        release_date = description_dict.get('발매일')
        genre = description_dict.get('장르')

        div_lyrics = soup.find('div', id='d_video_summary')

        lyrics = ''
        if div_lyrics:
            lyrics_list = []
            for item in div_lyrics:
                if item.name == 'br':
                    lyrics_list.append('\n')
                elif type(item) is NavigableString:
                    lyrics_list.append(item.strip())
            lyrics = ''.join(lyrics_list)

        # 리턴하지말고 데이터들을 자신의 속성으로 할당
        self.title = title
        self.artist = artist
        self.album = album
        self._release_date = release_date
        self._genre = genre
        self._lyrics = lyrics
        self._producers = {}

    @property
    def genre(self):
        if not self._genre:
            self.get_detail()
        return self._genre

    @property
    def lyrics(self):
        # 만약 가지고 있는 가사정보가 없다면
        if self._lyrics is None:
            # 받아와서 할당
            self.get_detail()
        # 그리고 가사정보 출력
        return self._lyrics

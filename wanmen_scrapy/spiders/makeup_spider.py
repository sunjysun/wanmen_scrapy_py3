import scrapy
import os
import json
import logging
from wanmen_scrapy.spiders.course_spider import CourseSpiderSpider
from wanmen_scrapy.custom.parse_json import get_m3u8_url


class MakeupSpiderSpider(CourseSpiderSpider):
    name = 'makeup_spider'
    allowed_domains = ['wanmen.org']
    '''#start_urls = ['http://*.wanmen.org/']
    course_content_url = 'https://api.wanmen.org/4.0/content/v2/courses/%s'
    course_lecture_url = 'https://api.wanmen.org/4.0/content/courses/%s/catalogue'
    lecture_video_url = 'https://api.wanmen.org/4.0/content/lectures/%s?routeId=main'
    
    headers = {
            'Origin': 'https://www.wanmen.org',
            'Referer': 'https://www.wanmen.org/',
            'content-type': 'application/json',
            'Authorization': 'Bearer xxxxxxxx',
    }
    
    def __init__(self, root_path='wanmen', info_only=True, *args, **kwargs):
        self.root_path = root_path  # 文件保存路径
        self.INFO_ONLY = int(info_only)
        '''
    def start_requests(self):
        walker = os.walk(self.root_path)
        while True:
            try:
                cur_dir, dirs, files = next(walker)
                # print(cur_dir)
                for fn in files:
                    if 'courses.json' == fn:
                        gnr = self.makeup_courses(cur_dir, dirs, fn)
                        while True:
                            try:
                                yield next(gnr)
                                continue
                            except StopIteration:
                                pass
                            break
                    elif 'lectures.json' == fn:
                        gnr = self.makeup_lectures(cur_dir, dirs, fn)
                        while True:
                            try:
                                yield next(gnr)
                                continue
                            except StopIteration:
                                pass
                            break
                continue
            except StopIteration:
                pass
            break
        
    def makeup_courses(self, cur_dir, dirs, fn):
        with open(os.path.join(cur_dir, fn)) as f:
            s = f.read()
        dic = json.loads(s)
        lst = dic['data']['category']['cateogry']['items']['categoryItem']
        lst_makeup = [itm for itm in lst if self.folder_name_filter([itm['name']])[0] not in dirs]
        for dic_course in lst_makeup:
            yield scrapy.Request(self.course_content_url % dic_course['id'], headers=self.headers, callback=self.parse_course_content)
        
    def makeup_lectures(self, cur_dir, dirs, fn):
        with open(os.path.join(cur_dir, fn)) as f:
            s = f.read()
        dic = json.loads(s)
        lst = dic['lectures']
        for dic_lecture in lst:
            lecture_prefix = dic_lecture['prefix']
            lecture_name = dic_lecture['name']
            lecture_prefix_name = '_'.join(self.folder_name_filter([f'第{lecture_prefix}讲', lecture_name]))
            lecture_path = os.path.join(cur_dir, lecture_prefix_name)
            lst_children = dic_lecture['children']
            for dic_child in lst_children:
                video_id = dic_child['_id']
                video_prefix = dic_child['prefix']
                video_name = dic_child['name']
                video_prefix_name = '_'.join(self.folder_name_filter([video_prefix, video_name]))
                video_path = os.path.join(lecture_path, video_prefix_name)
                need_makeup = False
                if os.path.isfile(os.path.join(video_path, f'{video_id}.json')):
                    m3u8_url = get_m3u8_url(os.path.join(video_path, f'{video_id}.json'))
                    m3u8_fn = None
                    quiz_fn = None
                    if m3u8_url is None:
                        quiz_pack_id = get_quiz_pack_id(os.path.join(video_path, f'{video_id}.json'))
                        quiz_fn = f'{quiz_pack_id}.quiz'
                    else:
                        m3u8_fn = m3u8_url.rsplit('?',1)[0].rsplit('/', 1)[1]
                    if m3u8_fn and os.path.isfile(os.path.join(video_path, m3u8_fn)) or quiz_fn and os.path.isfile(os.path.join(video_path, quiz_fn)):
                        pass
                    else:
                        logging.warning(f'{str(m3u8_fn)} {str(quiz_fn)} {video_path}')
                        need_makeup = True
                else:
                    logging.warning(os.path.join(video_path, f'{video_id}.json'))
                    need_makeup = True
                    
                if need_makeup:
                    yield scrapy.Request(self.lecture_video_url % (video_id), headers=self.headers, meta={'video_path': video_path, 'video_id': video_id}, callback=self.parse_video)
                else:
                    logging.info(f'完整: {video_path}')

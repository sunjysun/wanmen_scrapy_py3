# -*- coding: utf-8 -*-
import scrapy
import json
import os
import re
import codecs
from hashlib import md5
from wanmen_scrapy.items import *
from wanmen_scrapy.custom.parse_json import get_m3u8_url
from scrapy.shell import inspect_response


class CourseSpiderSpider(scrapy.Spider):
    name = 'course_spider'
    allowed_domains = ['wanmen.org']
    ''' - 2018-01-27 22:51:00
    - start_urls = ['https://api.wanmen.org/4.0/content/genres?webApp=web']
    - major_list_url = 'https://api.wanmen.org/4.0/content/majors?webApp=web'
    '''
    ''' - 2022-03-22 14:12:00
    - start_urls = ['https://api.wanmen.org/4.0/content/genres']
    - major_list_url = 'https://api.wanmen.org/4.0/content/majors'
    '''
    ''' + 2022-03-22 14:12:00 '''
    start_urls = ['https://endpoint.wanmen.org/graphql']
    ''' + end '''
    #count_per_page = 16
    #course_list_url = 'https://api.wanmen.org/4.0/content/courses?majorId=%s&page=%d&limit=%d'
    course_content_url = 'https://api.wanmen.org/4.0/content/v2/courses/%s'
    course_lecture_url = 'https://api.wanmen.org/4.0/content/courses/%s/catalogue'
    lecture_video_url = 'https://api.wanmen.org/4.0/content/lectures/%s?routeId=main'
    # root_path = r'E:\wanmen'
    dic_categories = dict()
    dic_majors = dict()
    dic_courses = dict()
    
    headers = {
            'Origin': 'https://www.wanmen.org',
            'Referer': 'https://www.wanmen.org/',
            'content-type': 'application/json',
            'Authorization': 'Bearer xxxxxxxx',
    }

    # app: uni mid inuka
    def __init__(self, root_path='wanmen', app='uni', info_only=True, *args, **kwargs):
        self.root_path = root_path  # 文件保存路径
        self.headers['x-app'] = app
        self.INFO_ONLY = int(info_only)

    def start_requests(self):
        body = '{"operationName":"CategoryProductsList","variables":{"isAll":true,"page":1,"pageSize":1088,"sortBy":"price","sortOrder":"desc","tags":[]},"query":"query CategoryProductsList($categoryId: String, $page: Int!, $pageSize: Int!, $sortBy: String!, $sortOrder: String!, $tags: [String!]) {\\n  category {\\n    cateogry(categoryId: $categoryId) {\\n      items(isAll: false, page: $page, pageSize: $pageSize, sortBy: $sortBy, sortOrder: $sortOrder, tags: $tags) {\\n        count\\n        categoryItem {\\n          id\\n          type\\n          name\\n          price\\n          description\\n          bigImage\\n          smallImage\\n          isPaid\\n          actions {\\n            watch\\n            download\\n            __typename\\n          }\\n          extra {\\n            hoursOfLesson\\n            teacherName\\n            openingAt\\n            state\\n            status\\n            informalInfo {\\n              price\\n              __typename\\n            }\\n            activity {\\n              name\\n              price\\n              originalPrice\\n              __typename\\n            }\\n            __typename\\n          }\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'
        
        yield scrapy.Request(self.start_urls[0], method="POST", headers=self.headers, body=body, callback=self.parse_course_list)
        
    def parse_course_list(self, response):
        dic = response.json()
        with open(os.path.join(self.root_path, 'courses.json'), 'wb') as f:
            f.write(response.body)
        #inspect_response(response, self)
        lst = dic['data']['category']['cateogry']['items']['categoryItem']
        for dic_course in lst:
            yield scrapy.Request(self.course_content_url % dic_course['id'], headers=self.headers, callback=self.parse_course_content)

    '''
    从课程页面解析当前课程所有视频信息
    '''
    def parse_course_content(self, response):
        # 获取url, 获取course_id，获取课程类别、专业、课程名
        url = response.url
        course_id = url.rsplit('/', 1)[1]

        #dic = json.loads(response.text)
        dic = response.json()
        #category_name = self.dic_courses[course_id]['category_name']
        #major_name = self.dic_courses[course_id]['major_name']
        course_name = dic['name']
        # 教师信息
        '''dic_teacher = dic['teacher']
        item_teacher = WanmenTeacherItem(
            ID=dic_teacher['id'],
            name=dic_teacher['name'],
            description=(dic_teacher['description'] if 'description' in dic_teacher.keys() else '')
        )
        # PPT等课程附件
        lst_doc = dic['documents']
        lst_doc_itm = []
        for dic_doc in lst_doc:
            lst_doc_itm.append(
                {
                    'name': dic_doc['name'],
                    'url': dic_doc['url']
                }
            )
        item_doc = WanmenDocItem(
            doc=lst_doc_itm
        )
        
        # 课程信息
        if 'price' in dic.keys():
            price=dic['price']
        else:
            price=-1
        item_course = WanmenCourseItem(
            ID=course_id,
            name=course_name,
            price=price,
            description=dic['description'],
            teacher=item_teacher,
            doc=item_doc
        )'''
        
        # 创建文件夹
        folder_lst = [self.root_path]
        #folder_lst.extend( self.folder_name_filter([category_name, major_name, course_name]))
        folder_lst.extend( self.folder_name_filter([course_name]))
        path = os.sep.join(folder_lst)
        if not os.path.isdir(path):
            os.makedirs(path)
        # 写入文件
        with open(os.sep.join([path, 'info.json']), 'wb') as f:
            #f.write(json.dumps(eval(str(item_course))))
            f.write(response.body)
        if dic.get('presentationVideo'):
            path_preguide = os.path.join(path, '先导片')
            if not os.path.isdir(path_preguide):
                os.makedirs(path_preguide)
            m3u8_url = get_m3u8_url(json_content=json.dumps(dic['presentationVideo']))
            yield scrapy.Request(m3u8_url, meta={'video_path': path_preguide}, headers=self.headers, callback=self.parse_m3u8)
        # 启动参数是否写只获取课程info，不再继续爬视频
        #if self.INFO_ONLY:
        #    return
            
        #parse_lecture

        yield scrapy.Request(self.course_lecture_url % (course_id), headers=self.headers, meta={'course_path': path}, callback=self.parse_lecture, priority=10)
        
    def parse_lecture(self, response):
        # 讲座信息
        course_path = response.meta['course_path']
        with open(os.sep.join([course_path, 'lectures.json']), 'wb') as f:
            f.write(response.body)
        dic = response.json()
        lst_lectures = dic['lectures']
        for dic_lecture in lst_lectures:
            lecture_prefix = dic_lecture['prefix']
            lecture_name = dic_lecture['name']
            lecture_prefix_name = '_'.join(self.folder_name_filter([f'第{lecture_prefix}讲', lecture_name]))
            lecture_path = os.path.join(course_path, lecture_prefix_name)
            lst_children = dic_lecture['children']
            for dic_child in lst_children:
                video_id = dic_child['_id']
                video_prefix = dic_child['prefix']
                video_name = dic_child['name']
                video_prefix_name = '_'.join(self.folder_name_filter([video_prefix, video_name]))
                video_path = os.path.join(lecture_path, video_prefix_name)
                yield scrapy.Request(self.lecture_video_url % (video_id), headers=self.headers, meta={'video_path': video_path, 'video_id': video_id}, callback=self.parse_video)
                
    def parse_video(self, response):
        video_path = response.meta['video_path']
        if not os.path.isdir(video_path):
            os.makedirs(video_path)
        with open(os.path.join(video_path, f'{response.meta["video_id"]}.json'), 'wb') as f:
            f.write(response.body)
        if response.json()['assetType'] == 'video':
            m3u8_url = get_m3u8_url(json_content=json.dumps(response.json()))
            yield scrapy.Request(m3u8_url, headers=self.headers, meta={'video_path': video_path}, callback=self.parse_m3u8, priority=20)
        elif response.json()['assetType'] == 'quiz':
            quiz_pack_id = response.json()['quizStatus']['quiz_pack_id']
            body = '{"operationName":"Quiz","variables":{"quizPackId":"' + quiz_pack_id + '","shuffle":true},"query":"query Quiz($quizPackId: String!, $shuffle: Boolean!) {\\n  lectureQuizPack(quizPackId: $quizPackId, shuffle: $shuffle) {\\n    id\\n    courseId\\n    lectureId\\n    quizzes {\\n      id\\n      quizPackId\\n      title\\n      explanation\\n      quizType\\n      options {\\n        id\\n        quizId\\n        description\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'
            yield scrapy.Request(self.start_urls[0], method='POST', headers=self.headers, body=body, meta={'video_path': video_path, 'quiz_pack_id': quiz_pack_id}, callback=self.parse_quiz)
        
    def parse_m3u8(self, response):
        with open(os.path.join(response.meta['video_path'], response.url.rsplit("?", 1)[0].rsplit("/", 1)[1]), 'wb') as f:
            f.write(response.body)
            
    def parse_quiz(self, response):
        with open(os.path.join(response.meta['video_path'], f'{response.meta["quiz_pack_id"]}.quiz'), 'wb') as f:
            f.write(response.body)
    
    
    @staticmethod
    def folder_name_filter(folder_name_lst):
        ret_lst = list()
        for folder_name in folder_name_lst:
            folder_name = folder_name.strip()
            folder_name = folder_name.replace('/', u'／')\
                                     .replace('\\', u'、')\
                                     .replace(':', u'：')\
                                     .replace('*', u'·')\
                                     .replace('?', u'？') \
                                     .replace('"', u'“') \
                                     .replace('<', u'《')\
                                     .replace('>', u'》')\
                                     .replace('|', u'¦')\
                                     .replace('\b', '')
            ret_lst.append(folder_name)
        if isinstance(folder_name_lst, str):
            ret_lst = ''.join(ret_lst)
        return ret_lst
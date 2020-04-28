# -*- coding:utf-8 -*-
__author__ = 'LiQiang'
__date__ = '2020/4/22 18:36'
import time
from uiautomator import Device
import pymongo


resource_id_dict = {
    'salary':'com.hpbr.bosszhipin:id/tv_salary_statue',
    'company':'com.hpbr.bosszhipin:id/tv_company_name',
    # 'address':'com.hpbr.bosszhipin:id/ll_area_and_distance',
    'scale':'com.hpbr.bosszhipin:id/tv_scale',
    'employer':'com.hpbr.bosszhipin:id/tv_employer'

}

client = pymongo.MongoClient('mongodb://root:123456@192.168.0.104:27017/')
db = client['spider']
collection = db['Boss']


device = Device('CSXDU17803007558')
device.wakeup()

bosspin_icon = device(text='BOSS直聘')

while not bosspin_icon.exists:
    device(scrollable=True).scroll.horiz.forward()
    bosspin_icon = device(text='BOSS直聘')
    time.sleep(1)

bosspin_icon.click()

device(scrollable=True).scroll.vert.toBeginning()

# device.swipe(500, 1710, 500, 385)
# time.sleep(2)
# device.swipe(500, 1710, 500, 385)

'''
# 点击搜索按钮
device.click(990,157)

input_box = device(resourceId='com.hpbr.bosszhipin:id/et_search')
if input_box.exists:
    input_box.set_text('python开发')
    device.press('enter')
else:
    print ("搜索框不存在")
time.sleep(2)
'''
# print(device(resourceId='com.hpbr.bosszhipin:id/view_job_card').count)
def crawl():
    for job in device(resourceId='com.hpbr.bosszhipin:id/view_job_card'):
        result_dict = {}
        job_info_box = job.child(resourceId='com.hpbr.bosszhipin:id/cl_position')
        job_name = job_info_box.child(resourceId='com.hpbr.bosszhipin:id/tv_position_name')
        if not job_name.exists:
            continue
        result_dict['job_name'] = job_name.text

        for key, resource_id in resource_id_dict.items():
            value = job.child(resourceId=resource_id)
            if not value.exists:
                continue
            result_dict[key] = value.text

        #地址
        address_box = job.child(resourceId='com.hpbr.bosszhipin:id/ll_area_and_distance')
        if not address_box.exists:
            continue
        result_dict['address'] = address_box.child(resourceId='com.hpbr.bosszhipin:id/tv_area_and_distance').text

        # 条件
        requires = job.child(resourceId='com.hpbr.bosszhipin:id/fl_require_info')
        if not requires.exists:
            continue

        require_info = []
        i = 0
        require_box = requires.child(index=i)
        while require_box.exists:
            # print (require_box.child(className='android.widget.TextView').text)
            require_info.append(require_box.child(className='android.widget.TextView').text)
            i = i + 1
            require_box = requires.child(index=i)

        result_dict['requires'] = require_info
        print (result_dict)
        # res.append(result_dict)
        # collection.insert_one(result_dict)
        collection.update({'job_name': result_dict.get('job_name'),'company':result_dict.get('company')}, {'$set': result_dict}, True)
        # print ('*'*20)


if __name__ == '__main__':
    while True:
        crawl()
        # device(scrollable=True).scroll.vert.forward()
        device.swipe(500, 1720, 500, 400)
        # time.sleep(3)
        time.sleep(4)





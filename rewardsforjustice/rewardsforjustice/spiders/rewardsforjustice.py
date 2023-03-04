import scrapy
import requests
import re
import datetime
import pandas as pd


class RewardsForJustice(scrapy.Spider):
    name = 'rewards'
    start_urls = ['https://rewardsforjustice.net/index/']
    page_num = 1
    max_num_pages = 1
    index = 0
    now = datetime.datetime.now()
    date_str = now.strftime('%Y%m%d_%H%M%S')
    data = []
   
    def parse (self, response):
        if self.page_num <= self.max_num_pages:                                      
            url = 'https://rewardsforjustice.net/index/'
            cookies = {
                'wp-wpml_current_language': 'en',
                '_ga': 'GA1.1.1181122383.1677801599',
                '_ga_BPR2J8V0QK': 'GS1.1.1677806317.2.1.1677806317.0.0.0',
            }
            headers = {
                'authority': 'rewardsforjustice.net',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'origin': 'https://rewardsforjustice.net',
                'referer': 'https://rewardsforjustice.net/index/?jsf=jet-engine:rewards-grid&tax=crime-category:1070%2C1071%2C1073%2C1072%2C1074',
                'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest',
            }
            params = {
                'jsf': 'jet-engine:rewards-grid',
                'tax': 'crime-category:1070,1071,1073,1072,1074',
                'nocache': '1677806315',
                'pagenum': str(self.page_num)
            }
            data = {
                'action': 'jet_engine_ajax',
                'handler': 'get_listing',
                'page_settings[post_id]': '22076',
                'page_settings[queried_id]': '22076|WP_Post',
                'page_settings[element_id]': 'ddd7ae9',
                'page_settings[page]': '1',
                'listing_type': 'elementor',
                'isEditMode': 'false',
                'addedPostCSS[]': '22078',
            }

            response = requests.post(url , params=params, cookies=cookies, headers=headers, data=data).json()
            if self.page_num == 1:
                self.max_num_pages = response['data']['filters_data']['props']['rewards-grid']['max_num_pages']

            selector = scrapy.Selector(text=response['data']['html'], type='html')  
            self.start_urls += selector.css('a.jet-engine-listing-overlay-link').xpath('@href').extract()

            print(f' \nSTATUS: Task: Scraping URLs, Page No: {self.page_num} of {self.max_num_pages}, URL Qty: {len(self.start_urls)-1}')

            self.page_num += 1
            next_page_url = f"{url}?pagenum={self.page_num}"
            yield scrapy.Request(next_page_url, cookies=cookies, headers=headers, callback=self.parse)

        elif (self.index == 0):
            print(' \nSTATUS: URL Sraping completed!!!')

            self.index += 1
            yield scrapy.Request(self.start_urls[self.index], callback=self.parse)

        else:
            print(f' \nSTATUS: Task: Scraping Page {self.index} of {len(self.start_urls) - 1}')

            # PAGE URL
            page_url = self.start_urls[self.index]

            # CATEGORY  
            category = 'null'

            # TITLE
            title_str = response.css('#hero-col > div > div.elementor-element.elementor-element-f2eae65.elementor-widget.elementor-widget-heading > div > h2::text').extract_first()
            title = title_str if title_str else 'null'

            # REWARD AMOUNT
            reward_str = response.css('#reward-box > div > div.elementor-element.elementor-element-5e60756.dc-has-condition.dc-condition-less.elementor-widget.elementor-widget-heading > div > h2::text').extract_first()
            reward_match = re.search(r'\$.+', reward_str) if reward_str else None
            reward_amount = reward_match.group() if reward_match else 'null'
            
            # ASSOCIATED ORGANIZATIONS
            org_str = response.css('#reward-fields > div > div.elementor-element.elementor-element-b7c9ae6.dc-has-condition.dc-condition-empty.elementor-widget.elementor-widget-text-editor > div::text').extract_first()
            org_match = re.findall(r"[^\s,][^,]*[^\s,]?", org_str) if org_str else None
            organizations = [match.strip() for match in org_match] if org_match else 'null'
            
            # ASSOCIATED LOCATIONS
            loc_str = response.css('#reward-fields > div > div.elementor-element.elementor-element-0fa6be9.dc-has-condition.dc-condition-empty.elementor-widget.elementor-widget-jet-listing-dynamic-terms > div > div > span::text').extract()           
            locations = re.findall(r"\b\w+\b", ''.join(loc_str)) if loc_str else 'null'

            # ABOUT
            about_list = response.css('#reward-about > div > div.elementor-element.elementor-element-52b1d20.elementor-widget.elementor-widget-theme-post-content > div').css('p::text').extract()
            about = about_list if len(about_list) > 0 else 'null'

            # IMAGE URL(S)
            image_url_list = response.css('#reward-fields > div > div.elementor-element.elementor-element-a819a24.dc-has-condition.dc-condition-empty.gallery-spacing-custom.terrorist-gallery.elementor-widget.elementor-widget-image-gallery > div > div').css('img::attr(src)').extract()
            image_url = image_url_list if len(image_url_list) > 0 else 'null'

            # DATE OF BIRTH (ISO FORMAT)
            dob_str = response.css('#reward-fields > div > div.elementor-element.elementor-element-9a896ea.dc-has-condition.dc-condition-empty.elementor-widget.elementor-widget-text-editor > div::text').extract_first()
            iso_date = 'null'
            if dob_str is not None:
                y = re.search(r'\d{4}', dob_str)
                m = re.search(r"January|February|March|April|May|June|July|August|September|October|November|December", dob_str)
                d = re.search(r'\b\d{1,2}\b', dob_str)
                year = y.group() if y else 'YYYY'
                month = m.group() if m else 'MM'
                day = d.group() if d else 'DD'
                if day != 'DD' and int(day) <= 9: day = '0' + day
                if month != 'MM':
                    month = str({
                        'January': '01', 'February': '02', 'March': '03',
                        'April': '04', 'May': '05', 'June': '06',
                        'July': '07', 'August': '08', 'September': '09',
                        'October': '10', 'November': '11', 'December': '12'
                    }[month])
                iso_date = f"{year}-{month}-{day}"

            page_data = {
                'Page URL': page_url,
                'Category': category,
                'Title': title,
                'Reward Amount': reward_amount,
                'Associated Organizations': organizations,
                'Associated Location(s)': locations,
                'About': about,
                'Image URL(s)': image_url,
                'Date Of Birth': iso_date
            }

            self.data.append(page_data)
            self.index += 1

            if self.index <= len(self.start_urls) - 1:
                yield scrapy.Request(self.start_urls[self.index], callback=self.parse)
            else:
                print(' \nSCRAPING COMPLETE!!!')               
                yield{'data': self.data}

                # Export Scrapy output to JSON and XLSX format
                print(' \nSTATUS: Exporting output to JSON and XLSX file format')
                df = pd.DataFrame(self.data)
                df.to_json(f'RWJST_{self.date_str}.json', orient='records')
                df.to_excel(f'RWJST_{self.date_str}.xlsx', index=False)
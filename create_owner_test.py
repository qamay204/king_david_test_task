import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import base64


class TestLoginForm(unittest.TestCase):

    def setUp(self):
        self.chrome_options = webdriver.ChromeOptions()
        # self.chrome_options.add_argument("headless")
        # self.chrome_options.add_argument("incognito")
        # self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.driver.set_window_size(1920, 1080)
        self.test_data = {
            'temp_data': ['paula47@example.com', '123456'],
            'first_login_url': 'http://client.roomizer.staging.thedevelopmentserver.com/#/expenses?filter=%7B%7D&order=DESC&page=1&perPage=10&sort=date',
            'owner_credentials': ['moisieievtest@gmail.com', '1q2w3e4r5t'],
            'final_url': 'http://owners.roomizer.staging.thedevelopmentserver.com/#/expenses'
        }

    def tearDown(self):
        self.driver.quit()

    @staticmethod
    def get_confirm_mail():
        SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)
        service = build('gmail', 'v1', http=creds.authorize(Http()))

        # Call the Gmail API to fetch INBOX
        results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
        messages = results.get('messages', [])

        if not messages:
            print("No messages found.")
        else:
            print("Message snippets:")
            link = ''
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id'], format='raw').execute()
                msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
                if 'http://owners.roomizer.staging.thedevelopmentserver.com/#' in str(msg_str):
                    start_index = str(msg_str).find('[http')
                    end_index = str(msg_str).find(']', start_index)

                    print(str(msg_str)[start_index+1:end_index])
                    link = str(msg_str)[start_index+1:end_index]
                    print('Link in func:', link)
                    clear_link = link.replace('=\\r\\n', '')
                    clear_link = clear_link.replace('3D', '')
                    return clear_link
            # link = link.replace('=\r\n', '')
            # return link

    def test_create_owner(self):
        driver = self.driver
        # Switch to the new window and open URL B
        driver.get('http://client.roomizer.staging.thedevelopmentserver.com/#/login')
        driver.find_element_by_id('username').send_keys(self.test_data['temp_data'][0])
        driver.find_element_by_id('password').send_keys(self.test_data['temp_data'][1])
        driver.find_element_by_tag_name('button').click()
        time.sleep(1.8)
        self.assertEqual(driver.current_url, self.test_data['first_login_url'])
        driver.find_element(By.XPATH, '//a[contains(., "Owners")]').click()
        driver.find_element_by_xpath('//span[contains(., "Create")]').click()
        driver.find_element_by_id('first_name').send_keys('Andrii')
        driver.find_element_by_id('last_name').send_keys('Moisieiev')
        driver.find_element_by_id('email').send_keys(self.test_data['owner_credentials'][0])
        driver.find_element_by_id('start_balance_date').click()
        driver.find_element_by_xpath("//p[contains(., '31')]").click()
        driver.find_element_by_id('start_balance_amount').clear()
        driver.find_element_by_id('start_balance_amount').send_keys(5000)
        driver.find_element_by_id('currency_id').click()
        driver.find_element_by_xpath('//li[contains(., "EUR")]').click()
        driver.find_element_by_id('is_active').click()
        driver.find_element_by_id('send_email_verification').click()
        driver.find_element_by_xpath('//span[contains(., "Save")]').click()
        time.sleep(5)
        # -----------------------------------------
        driver.get(TestLoginForm.get_confirm_mail()) # take confirm link from function
        driver.find_elements_by_xpath('//*[@id="password"]')[0].send_keys(self.test_data['owner_credentials'][1])
        driver.find_elements_by_xpath('//*[@id="password"]')[1].send_keys(self.test_data['owner_credentials'][1])
        driver.find_element_by_xpath('//*[@id="root"]/div/div/div/form/div[2]/button/span[1]').click()
        driver.find_element_by_id('username').send_keys(self.test_data['owner_credentials'][0])
        driver.find_element_by_id('password').send_keys(self.test_data['owner_credentials'][1])
        driver.find_element_by_xpath('//span[contains(., "Sign in")]').click()
        time.sleep(2)
        self.assertEqual(driver.current_url, self.test_data['final_url'])


if __name__ == '__main__':
    unittest.main()










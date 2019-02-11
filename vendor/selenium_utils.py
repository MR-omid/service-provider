from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from vendor.custom_exception import TimeoutResponseError


def go_to(driver, url):
    try:
        driver.get(url)
    except TimeoutException:
        raise TimeoutResponseError('Page load Timeout Occured')


def refresh_page(driver):
    try:
        driver.refresh()
    except TimeoutException:
        raise TimeoutResponseError('Page load Timeout Occured')


def check_exists_by_xpath(element, xpath):
    try:
        element.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


def check_exists_by_css_selector(element, selector):
    try:
        element.find_element_by_css_selector(selector)
    except NoSuchElementException:
        return False
    return True


def check_exists_by_tag_name(element, tag):
    try:
        element.find_element_by_tag_name(tag)
    except NoSuchElementException:
        return False
    return True


def check_click(element):
    try:
        element.click()
    except:
        return False
    return True


def _by_xpath(element, xpath):
    try:
        return element.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False


def _by_css_selector(element, selector):
    try:
        return element.find_element_by_css_selector(selector)
    except NoSuchElementException:
        return False


def _by_tag_name(element, tag):
    try:
        return element.find_element_by_tag_name(tag)
    except NoSuchElementException:
        return False


def _by_xpath_s(element, xpath):
    try:
        return element.find_elements_by_xpath(xpath)
    except NoSuchElementException:
        return False


def _by_css_selector_s(element, selector):
    try:
        return element.find_elements_by_css_selector(selector)
    except NoSuchElementException:
        return False


def _by_tag_name_s(element, tag):
    try:
        return element.find_elements_by_tag_name(tag)
    except NoSuchElementException:
        return False


def _click(element):
    try:
        return element.click()
    except:
        return False


def search(driver, search_value):
    search_bar = _by_xpath(driver,
                           '/html/body/nav/div/form/div/div/div/artdeco-typeahead-deprecated/artdeco-typeahead-deprecated-input/input')
    if search_bar:
        search_bar.send_keys(Keys.CONTROL, "a")
        search_bar.send_keys(search_value)
        search_click = _by_xpath(driver, '/html/body/nav/div/form/div/div/div/div/button')
        if search_click:
            search_click.click()


def exatract_results(driver):
    result = []
    div_result = _by_css_selector(driver, '.blended-srp-results-js.pt0.pb4.ph0.container-with-shadow')
    if div_result:
        ul_result = _by_css_selector(div_result, '.search-results__list.list-style-none.mt2')
        if ul_result:
            li_results = _by_xpath_s(ul_result, './li')
            for li in li_results:
                person = {'data': '', 'type': 5, 'property': [], 'special': [{'type': 0, 'sub_type': 4}]}
                div = _by_xpath(li, './div/div/div[2]')
                if div:
                    a = _by_xpath(div, './a')
                    if a:
                        account_id = a.get_attribute('href')
                        print(account_id)
                        person['property'].append({'ref': account_id})
                        name = _by_xpath(a, './h3/span/span[1]/span[1]')
                        if name:
                            print(name.text)
                            person['data'] = name.text
                    title = _by_xpath(div, './p[1]/span')
                    if title:
                        print(title.text)
                        person['property'].append({'title': title.text})
                    location = _by_xpath(div, './p[2]/span')
                    if location:
                        print(location.text)
                        person['property'].append({'location': location.text})
                result.append(person)
    return result


def click_next(driver):
    div_results = _by_css_selector(driver, '.blended-srp-results-js.pt0.pb4.ph0.container-with-shadow')
    if div_results:
        div = _by_xpath(div_results, './div[1]')
        if div:
            temp = _by_tag_name(div, 'artdeco-pagination')
            if temp:
                next_button = _by_xpath(temp, './button[2]')
                if next_button:
                    if next_button.get_attribute('disabled'):
                        return False
                    else:
                        driver.execute_script("arguments[0].click();", next_button)
                        return True

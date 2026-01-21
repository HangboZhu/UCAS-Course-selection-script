from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from matplotlib import pyplot as plt
import ddddocr
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
import argparse
import chromedriver_autoinstaller
import re

from utils import driverOption, click, dataCollection


parser = argparse.ArgumentParser()
parser.add_argument('username')
parser.add_argument('password')
parser.add_argument('subjectID')
parser.add_argument('courseID')
parser.add_argument('--noCaptcha', action='store_true')
args = parser.parse_args()


# 自动安装适配版本的 ChromeDriver，并返回其路径
driver_path = chromedriver_autoinstaller.install()
print("ChromeDriver 路径：", driver_path)

driver = webdriver.Chrome(driver_path, options=driverOption())

driver.get('https://sep.ucas.ac.cn/')

# 登录循环
login_success = False
max_retries = 10
retry_count = 0

while not login_success and retry_count < max_retries:
    try:
        retry_count += 1
        print(f"\n=== 登录尝试 {retry_count}/{max_retries} ===")

        # 等待登录页面元素加载
        wait = WebDriverWait(driver, 10)

        # 检查是否已经登录成功
        current_url = driver.current_url
        if current_url and 'appStore' in current_url:
            print("✓ 检测到已登录,跳过登录步骤")
            login_success = True
            break

        # 等待用户名输入框出现
        print("等待登录页面加载...")
        username_input = wait.until(EC.presence_of_element_located((By.ID, 'userName1')))
        password_input = wait.until(EC.presence_of_element_located((By.ID, 'pwd1')))

        # 清空输入框(防止重复输入)
        username_input.clear()
        password_input.clear()

        print("输入用户名和密码...")
        username_input.send_keys(args.username)
        password_input.send_keys(args.password)

        print("点击登录按钮...")
        login_button = driver.find_element(By.ID, 'sb1')
        login_button.click()

        # 等待登录结果
        print("等待登录结果...")
        sleep(1)

        # 检查是否登录成功
        current_url = driver.current_url
        if current_url and 'appStore' in current_url:
            print("✓ 登录成功!")
            login_success = True
        else:
            print("✗ 登录失败(可能是验证码错误)，重新尝试...")
            driver.get('https://sep.ucas.ac.cn/')
            sleep(2)

    except Exception as e:
        print(f"✗ 登录过程出错: {str(e)[:100]}")
        print("正在重新加载登录页面...")
        try:
            driver.get('https://sep.ucas.ac.cn/')
            sleep(2)
        except:
            print("✗ 浏览器可能已关闭，退出程序")
            exit(1)

if not login_success:
    print(f"\n✗ 登录失败: 已尝试 {max_retries} 次")
    exit(1)

sleep(1)

# 点击"选课"链接进入选课系统
# 保存当前窗口句柄
main_window = driver.current_window_handle

# 等待页面完全加载,等待"选课"链接出现并可点击
wait = WebDriverWait(driver, 10)

try:
    # 方法1: 通过链接文本定位
    print("尝试定位'选课'链接...")
    select_course_link = wait.until(
        EC.element_to_be_clickable((By.LINK_TEXT, '选课'))
    )
    print("找到'选课'链接,准备点击...")
except:
    try:
        # 方法2: 通过部分href属性定位
        print("尝试通过href定位'选课'链接...")
        select_course_link = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href*="/portal/site/524/2412"]'))
        )
        print("找到'选课'链接,准备点击...")
    except:
        # 方法3: 通过XPath定位
        print("尝试通过XPath定位'选课'链接...")
        select_course_link = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "选课") and contains(@href, "/portal/site/524/2412")]'))
        )
        print("找到'选课'链接,准备点击...")

# 先尝试滚动到元素可见位置
driver.execute_script("arguments[0].scrollIntoView(true);", select_course_link)
sleep(0.5)

# 使用JavaScript点击以确保onclick事件被触发
driver.execute_script("arguments[0].click();", select_course_link)
print("已点击'选课'链接")

sleep(3)

# 切换到新打开的标签页
for window_handle in driver.window_handles:
    if window_handle != main_window:
        driver.switch_to.window(window_handle)
        break

# 等待新页面加载
wait = WebDriverWait(driver, 3)
wait.until(EC.url_contains('xkgo.ucas.ac.cn'))

print("选课页面已加载，等待页面初始化...")
sleep(2)

# 点击"新增加本学期研究生课程"按钮
print("查找并点击'新增加本学期研究生课程'按钮...")
try:
    # 尝试多种方式定位按钮
    try:
        # 方法1: 通过按钮文本内容定位
        add_course_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '新增加本学期研究生课程')]"))
        )
        print("✓ 通过文本找到按钮")
    except:
        try:
            # 方法2: 通过form id和button属性定位
            add_course_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//form[@id='regfrm2']//button[@type='submit']"))
            )
            print("✓ 通过form找到按钮")
        except:
            # 方法3: 查找所有提交按钮,选择包含"新增"的
            add_course_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit'][contains(., '新增')]"))
            )
            print("✓ 通过submit类型找到按钮")

    print("准备点击按钮...")
    driver.execute_script("arguments[0].scrollIntoView(true);", add_course_button)
    sleep(0.5)

    # 使用JavaScript点击确保成功
    driver.execute_script("arguments[0].click();", add_course_button)
    print("✓ 已点击'新增加本学期研究生课程'按钮")
    sleep(3)  # 增加等待时间,让页面完全加载

except Exception as e:
    print(f"✗ 查找或点击按钮失败: {str(e)[:200]}")
    print("尝试打印页面源码以调试...")
    # 保存页面源码用于调试
    with open('debug_page.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    print("页面源码已保存到 debug_page.html")
    exit(1)

# 输入课程编码进行查询（只查询一次）
print(f"输入课程编码: {args.courseID}")

# 增加等待时间，确保页面元素加载完成
wait = WebDriverWait(driver, 5)  # 增加超时时间到15秒

try:
    # 等待课程编码输入框出现
    print("等待课程编码输入框加载...")
    course_code_input = wait.until(EC.presence_of_element_located((By.ID, 'courseCode')))
    print("✓ 找到课程编码输入框")

    course_code_input.clear()
    course_code_input.send_keys(args.courseID)
    print("✓ 已输入课程编码")

    # 点击查询按钮
    query_button = wait.until(EC.element_to_be_clickable((By.ID, 'submitBtn')))
    query_button.click()
    print("✓ 已点击查询按钮")

    sleep(3)  # 等待查询结果加载

except Exception as e:
    print(f"✗ 查询课程失败: {str(e)[:200]}")
    print("保存当前页面用于调试...")
    with open('debug_course_query.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    print("页面源码已保存到 debug_course_query.html")
    exit(1)

# 开始抢课循环
print("开始监控课程是否有空位...")
while True:
    try:
        # 等待查询结果出现，选择第一个课程的checkbox
        first_course_checkbox = wait.until(
            EC.presence_of_element_located((By.XPATH, "//table//tbody/tr[1]//input[@type='checkbox']"))
        )

        if first_course_checkbox.is_enabled():
            print(f"[{datetime.datetime.now()}] ✓ 找到空位！准备选择课程...")
            driver.execute_script("$(arguments[0]).click()", first_course_checkbox)
            print("✓ 已选择课程")
            break  # 跳出循环，进入提交流程
        else:
            print(f"[{datetime.datetime.now()}] 课程已满，3秒后刷新重试...")
            sleep(3)
            driver.refresh()
            sleep(1)  # 等待页面刷新完成

    except Exception as e:
        print(f"[{datetime.datetime.now()}] 检查课程时出错，刷新重试...")
        sleep(3)
        driver.refresh()
        sleep(1)

# 提交选课循环（处理验证码错误重试）
max_submit_retries = 10
submit_retry_count = 0
submit_success = False

while submit_retry_count < max_submit_retries and not submit_success:
    try:
        submit_retry_count += 1
        print(f"\n=== 第 {submit_retry_count} 次尝试提交选课 ===")

        # 选中课程后，进入提交流程
        sleep(1)

        # 滚动到页面底部查看验证码
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        print("等待验证码加载...")
        sleep(1)

        # OCR识别验证码（带重试机制）
        max_ocr_retries = 5
        ocr_retry_count = 0
        res = None

        # 使用ddddocr默认模式识别纯数字
        ocr = ddddocr.DdddOcr(show_ad=False)

        while ocr_retry_count < max_ocr_retries:
            try:
                ocr_retry_count += 1
                print(f"尝试识别验证码 ({ocr_retry_count}/{max_ocr_retries})...")

                ocrImage = driver.find_element(By.ID, 'adminValidateImg')
                ocrImage.screenshot('ocrCal.png')

                # 直接读取图片并识别
                with open('ocrCal.png', 'rb') as f:
                    image_bytes = f.read()

                result = ocr.classification(image_bytes)
                print(f"OCR原始识别结果: '{result}'")

                # 提取纯数字（保持字符串格式，不转为int）
                numbers = re.findall(r'\d+', result)
                if numbers:
                    res = ''.join(numbers)  # 保持字符串格式，保留前导零
                    print(f"✓ 提取数字结果: {res}")
                    break
                else:
                    raise ValueError(f"未识别到数字，识别结果为: {result}")

            except Exception as e:
                print(f"✗ 验证码识别失败: {str(e)[:100]}")
                if ocr_retry_count < max_ocr_retries:
                    print("点击验证码图片刷新...")
                    try:
                        ocrImage = driver.find_element(By.ID, 'adminValidateImg')
                        ocrImage.click()  # 点击验证码图片刷新
                        sleep(1)
                    except:
                        pass
                else:
                    print("验证码识别失败次数过多")
                    res = None
                    break

        if res is not None:
            # 输入验证码
            vcode = driver.find_element(By.ID, 'vcode')
            vcode.clear()
            vcode.send_keys(str(res))
            print("✓ 已输入验证码")

            # 提交选课 - 使用正确的按钮ID
            submit_button = driver.find_element(By.ID, 'submitCourse')
            submit_button.click()
            print("✓ 已点击提交选课按钮")

            sleep(2)

            # 检查是否有验证码错误提示
            try:
                error_msg = driver.find_element(By.ID, 'messageBoxError')
                if error_msg.is_displayed():
                    error_text = driver.find_element(By.ID, 'loginError').text
                    print(f"✗ 提交失败: {error_text}")
                    print("准备重新提交...")

                    # 刷新页面重新开始
                    driver.refresh()
                    sleep(2)

                    # 重新输入课程编码并查询
                    course_code_input = wait.until(EC.presence_of_element_located((By.ID, 'courseCode')))
                    course_code_input.clear()
                    course_code_input.send_keys(args.courseID)
                    print("✓ 重新输入课程编码")

                    query_button = wait.until(EC.element_to_be_clickable((By.ID, 'submitBtn')))
                    query_button.click()
                    print("✓ 重新点击查询按钮")
                    sleep(2)

                    # 重新选择课程checkbox
                    first_course_checkbox = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//table//tbody/tr[1]//input[@type='checkbox']"))
                    )
                    driver.execute_script("$(arguments[0]).click()", first_course_checkbox)
                    print("✓ 重新选择课程")

                    continue  # 继续下一次循环尝试
            except:
                # 没有错误提示，说明可能提交成功了
                pass

            # 点击确定按钮（弹窗确认）
            try:
                confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='确定']")))
                confirm_button.click()
                print("✓ 已确认提交")
            except:
                print("未找到确认按钮，可能已直接提交成功")

            print(f'[{datetime.datetime.now()}] ✓ 选课提交完成！')
            print(f'[{datetime.datetime.now()}] ✓ 选课成功！')
            submit_success = True
            break

        else:
            print("验证码识别失败，刷新页面重试...")
            driver.refresh()
            sleep(2)

            # 重新输入课程编码并查询
            course_code_input = wait.until(EC.presence_of_element_located((By.ID, 'courseCode')))
            course_code_input.clear()
            course_code_input.send_keys(args.courseID)

            query_button = wait.until(EC.element_to_be_clickable((By.ID, 'submitBtn')))
            query_button.click()
            sleep(2)

            # 重新选择课程
            first_course_checkbox = wait.until(
                EC.presence_of_element_located((By.XPATH, "//table//tbody/tr[1]//input[@type='checkbox']"))
            )
            driver.execute_script("$(arguments[0]).click()", first_course_checkbox)

    except Exception as e:
        print(f"✗ 提交选课时出错: {str(e)[:200]}")
        print("保存当前页面用于调试...")
        with open('debug_submit_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("页面源码已保存到 debug_submit_error.html")

        # 刷新页面重试
        print("刷新页面，准备重试...")
        driver.refresh()
        sleep(2)

        try:
            # 重新输入课程编码并查询
            course_code_input = wait.until(EC.presence_of_element_located((By.ID, 'courseCode')))
            course_code_input.clear()
            course_code_input.send_keys(args.courseID)

            query_button = wait.until(EC.element_to_be_clickable((By.ID, 'submitBtn')))
            query_button.click()
            sleep(2)

            # 重新选择课程
            first_course_checkbox = wait.until(
                EC.presence_of_element_located((By.XPATH, "//table//tbody/tr[1]//input[@type='checkbox']"))
            )
            driver.execute_script("$(arguments[0]).click()", first_course_checkbox)
        except:
            print("重试失败，跳过此次尝试")

if not submit_success:
    print(f"\n✗ 选课失败: 已尝试 {max_submit_retries} 次")
    print("请手动完成选课")

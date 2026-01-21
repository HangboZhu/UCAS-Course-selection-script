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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

from utils import driverOption, click, dataCollection

# 加载环境变量
load_dotenv()

# 邮件配置
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.163.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '465'))
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')


def send_email_notification(course_id, success=True):
    """发送选课结果邮件通知"""
    try:
        if not all([SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL]):
            print("⚠️  邮箱配置不完整，跳过邮件通知")
            return

        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f'【UCAS选课通知】{"成功" if success else "失败"}'

        # 邮件正文
        if success:
            body = f"""
            <html>
            <body>
                <h2 style="color: green;">✅ 选课成功！</h2>
                <p><strong>课程编码：</strong>{course_id}</p>
                <p><strong>选课时间：</strong>{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>恭喜您成功抢到课程！</p>
                <hr>
                <p style="color: gray; font-size: 12px;">此邮件由UCAS选课脚本自动发送</p>
            </body>
            </html>
            """
        else:
            body = f"""
            <html>
            <body>
                <h2 style="color: red;">❌ 选课失败</h2>
                <p><strong>课程编码：</strong>{course_id}</p>
                <p><strong>时间：</strong>{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>选课未能成功，请手动检查。</p>
                <hr>
                <p style="color: gray; font-size: 12px;">此邮件由UCAS选课脚本自动发送</p>
            </body>
            </html>
            """

        msg.attach(MIMEText(body, 'html'))

        # 发送邮件
        print(f"正在发送邮件到 {RECIPIENT_EMAIL}...")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("✓ 邮件发送成功！")

    except Exception as e:
        print(f"✗ 邮件发送失败: {str(e)[:100]}")
        print("请检查邮箱配置是否正确")


def main(username, password, subject_id, course_id):
    """主函数：执行UCAS选课流程"""

    # 自动安装适配版本的 ChromeDriver，并返回其路径
    driver_path = chromedriver_autoinstaller.install()
    print("ChromeDriver 路径：", driver_path)

    driver = webdriver.Chrome(driver_path, options=driverOption())

    try:
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
                username_input.send_keys(username)
                password_input.send_keys(password)

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
                    return False

        if not login_success:
            print(f"\n✗ 登录失败: 已尝试 {max_retries} 次")
            return False

        sleep(1)

        # 点击"选课"链接进入选课系统
        main_window = driver.current_window_handle
        wait = WebDriverWait(driver, 10)

        try:
            print("尝试定位'选课'链接...")
            select_course_link = wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, '选课'))
            )
            print("找到'选课'链接,准备点击...")
        except:
            try:
                print("尝试通过href定位'选课'链接...")
                select_course_link = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href*="/portal/site/524/2412"]'))
                )
                print("找到'选课'链接,准备点击...")
            except:
                print("尝试通过XPath定位'选课'链接...")
                select_course_link = wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "选课") and contains(@href, "/portal/site/524/2412")]'))
                )
                print("找到'选课'链接,准备点击...")

        driver.execute_script("arguments[0].scrollIntoView(true);", select_course_link)
        sleep(0.5)
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
            try:
                add_course_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '新增加本学期研究生课程')]"))
                )
                print("✓ 通过文本找到按钮")
            except:
                try:
                    add_course_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//form[@id='regfrm2']//button[@type='submit']"))
                    )
                    print("✓ 通过form找到按钮")
                except:
                    add_course_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit'][contains(., '新增')]"))
                    )
                    print("✓ 通过submit类型找到按钮")

            print("准备点击按钮...")
            driver.execute_script("arguments[0].scrollIntoView(true);", add_course_button)
            sleep(0.5)
            driver.execute_script("arguments[0].click();", add_course_button)
            print("✓ 已点击'新增加本学期研究生课程'按钮")
            sleep(3)

        except Exception as e:
            print(f"✗ 查找或点击按钮失败: {str(e)[:200]}")
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("页面源码已保存到 debug_page.html")
            return False

        # 输入课程编码进行查询（只查询一次）
        print(f"输入课程编码: {course_id}")
        wait = WebDriverWait(driver, 5)

        try:
            print("等待课程编码输入框加载...")
            course_code_input = wait.until(EC.presence_of_element_located((By.ID, 'courseCode')))
            print("✓ 找到课程编码输入框")

            course_code_input.clear()
            course_code_input.send_keys(course_id)
            print("✓ 已输入课程编码")

            query_button = wait.until(EC.element_to_be_clickable((By.ID, 'submitBtn')))
            query_button.click()
            print("✓ 已点击查询按钮")

            sleep(3)

        except Exception as e:
            print(f"✗ 查询课程失败: {str(e)[:200]}")
            with open('debug_course_query.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("页面源码已保存到 debug_course_query.html")
            return False

        # 开始抢课循环
        print("开始监控课程是否有空位...")
        while True:
            try:
                first_course_checkbox = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//table//tbody/tr[1]//input[@type='checkbox']"))
                )

                if first_course_checkbox.is_enabled():
                    print(f"[{datetime.datetime.now()}] ✓ 找到空位！准备选择课程...")
                    driver.execute_script("$(arguments[0]).click()", first_course_checkbox)
                    print("✓ 已选择课程")
                    break
                else:
                    print(f"[{datetime.datetime.now()}] 课程已满，3秒后刷新重试...")
                    sleep(3)
                    driver.refresh()
                    sleep(1)

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

                sleep(1)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                print("等待验证码加载...")
                sleep(1)

                # OCR识别验证码
                max_ocr_retries = 5
                ocr_retry_count = 0
                res = None

                ocr = ddddocr.DdddOcr(show_ad=False)

                while ocr_retry_count < max_ocr_retries:
                    try:
                        ocr_retry_count += 1
                        print(f"尝试识别验证码 ({ocr_retry_count}/{max_ocr_retries})...")

                        ocrImage = driver.find_element(By.ID, 'adminValidateImg')
                        ocrImage.screenshot('ocrCal.png')

                        with open('ocrCal.png', 'rb') as f:
                            image_bytes = f.read()

                        result = ocr.classification(image_bytes)
                        print(f"OCR原始识别结果: '{result}'")

                        numbers = re.findall(r'\d+', result)
                        if numbers:
                            res = ''.join(numbers)
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
                                ocrImage.click()
                                sleep(1)
                            except:
                                pass
                        else:
                            print("验证码识别失败次数过多")
                            res = None
                            break

                if res is not None:
                    vcode = driver.find_element(By.ID, 'vcode')
                    vcode.clear()
                    vcode.send_keys(str(res))
                    print("✓ 已输入验证码")

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

                            driver.refresh()
                            sleep(2)

                            course_code_input = wait.until(EC.presence_of_element_located((By.ID, 'courseCode')))
                            course_code_input.clear()
                            course_code_input.send_keys(course_id)
                            print("✓ 重新输入课程编码")

                            query_button = wait.until(EC.element_to_be_clickable((By.ID, 'submitBtn')))
                            query_button.click()
                            print("✓ 重新点击查询按钮")
                            sleep(2)

                            first_course_checkbox = wait.until(
                                EC.presence_of_element_located((By.XPATH, "//table//tbody/tr[1]//input[@type='checkbox']"))
                            )
                            driver.execute_script("$(arguments[0]).click()", first_course_checkbox)
                            print("✓ 重新选择课程")

                            continue
                    except:
                        pass

                    # 点击确定按钮
                    try:
                        confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='确定']")))
                        confirm_button.click()
                        print("✓ 已确认提交")
                    except:
                        print("未找到确认按钮，可能已直接提交成功")

                    print(f'[{datetime.datetime.now()}] ✓ 选课提交完成！')
                    print(f'[{datetime.datetime.now()}] ✓ 选课成功！')
                    submit_success = True

                    # 发送邮件通知
                    send_email_notification(course_id, success=True)

                    break

                else:
                    print("验证码识别失败，刷新页面重试...")
                    driver.refresh()
                    sleep(2)

                    course_code_input = wait.until(EC.presence_of_element_located((By.ID, 'courseCode')))
                    course_code_input.clear()
                    course_code_input.send_keys(course_id)

                    query_button = wait.until(EC.element_to_be_clickable((By.ID, 'submitBtn')))
                    query_button.click()
                    sleep(2)

                    first_course_checkbox = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//table//tbody/tr[1]//input[@type='checkbox']"))
                    )
                    driver.execute_script("$(arguments[0]).click()", first_course_checkbox)

            except Exception as e:
                print(f"✗ 提交选课时出错: {str(e)[:200]}")
                with open('debug_submit_error.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print("页面源码已保存到 debug_submit_error.html")

                print("刷新页面，准备重试...")
                driver.refresh()
                sleep(2)

                try:
                    course_code_input = wait.until(EC.presence_of_element_located((By.ID, 'courseCode')))
                    course_code_input.clear()
                    course_code_input.send_keys(course_id)

                    query_button = wait.until(EC.element_to_be_clickable((By.ID, 'submitBtn')))
                    query_button.click()
                    sleep(2)

                    first_course_checkbox = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//table//tbody/tr[1]//input[@type='checkbox']"))
                    )
                    driver.execute_script("$(arguments[0]).click()", first_course_checkbox)
                except:
                    print("重试失败，跳过此次尝试")

        if not submit_success:
            print(f"\n✗ 选课失败: 已尝试 {max_submit_retries} 次")
            print("请手动完成选课")
            send_email_notification(course_id, success=False)
            return False

        return True

    finally:
        # 保持浏览器窗口打开，让用户查看结果
        print("\n脚本执行完成，浏览器窗口将保持打开...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='UCAS选课自动抢课脚本')
    parser.add_argument('username', help='用户名（邮箱）')
    parser.add_argument('password', help='密码')
    parser.add_argument('subjectID', help='学院ID（暂未使用）')
    parser.add_argument('courseID', help='课程编码')
    parser.add_argument('--noCaptcha', action='store_true', help='无验证码模式（暂未使用）')

    args = parser.parse_args()

    # 调用主函数
    success = main(args.username, args.password, args.subjectID, args.courseID)

    if success:
        print("\n🎉 选课成功！")
    else:
        print("\n❌ 选课失败，请检查日志")

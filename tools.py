import subprocess
import time

mb_app_activity_list = [
'com.whatsapp/com.whatsapp.Main',
'com.amazon.mShop.android.shopping/com.amazon.mShop.home.HomeActivity',
'org.telegram.messenger/org.telegram.ui.LaunchActivity',
'us.zoom.videomeetings/com.zipow.videobox.LauncherActivity',
'com.instagram.android/com.instagram.android.activity.MainTabActivity',
'jp.naver.line.android/jp.naver.line.android.activity.SplashActivity',
'com.google.android.apps.maps/com.google.android.maps.MapsActivity',
'com.google.android.apps.docs.editors.docs/com.google.android.apps.docs.app.NewMainProxyActivity',
'com.google.android.gm/com.google.android.gm.ConversationListActivityGmail',
'com.facebook.katana/com.facebook.katana.LoginActivity',
'com.quora.android/com.quora.android.components.activities.LauncherActivity',
'com.reddit.frontpage/launcher.default',
'com.linkedin.android/com.linkedin.android.infra.navigation.MainActivity',
'com.adobe.reader/.AdobeReader',
'com.openai.chatgpt/com.openai.chatgpt.MainActivity',
]

mb_app_package_list = [i.split('/')[0] for i in mb_app_activity_list]


gb_app_activity_list = [
'com.booking/com.booking.startup.HomeActivity',
'com.tencent.ig/com.epicgames.ue4.SplashActivity',
'com.adobe.psmobile/com.adobe.psmobile.SplashScreen',
'com.twitter.android/com.twitter.android.StartActivity',
'com.zhiliaoapp.musically/com.ss.android.ugc.aweme.splash.SplashActivity',
'com.xingin.xhs/com.xingin.xhs.index.v2.IndexActivityV2',
'com.lemon.lvoverseas/com.vega.main.MainActivity',
'com.campmobile.snow/com.linecorp.b612.android.activity.ActivityCamera',
'com.google.earth/com.google.android.apps.earth.flutter.EarthFlutterActivity',
'com.roblox.client/com.roblox.client.startup.ActivitySplash',
'com.tinder/com.tinder.launch.internal.activities.LoginActivity',
'com.einnovation.temu/com.baogong.splash.activity.MainFrameActivity',
'com.ubercab/com.ubercab.presidio.app.core.root.RootActivity',
]


gb_app_package_list = [i.split('/')[0] for i in gb_app_activity_list]

package_to_name = {
    'com.booking':'Booking',
    'com.tencent.ig':'PUBG',
    'com.adobe.psmobile':'Photoshop',
    'com.twitter.android':'Twitter',
    'com.zhiliaoapp.musically':'TikTok',
    'com.xingin.xhs':'RedNote',
    'com.lemon.lvoverseas':'Capcut',
    'com.campmobile.snow':'Snow',
    'com.google.earth':"GoogleEarth",
    'com.roblox.client':"Roblox",
    'com.tinder':"Tinder",
    "com.einnovation.temu":"Temu",
    'com.ubercab':"Uber"
}


def open_app(activity_name,output_file=None):
    """
    打开指定的 Android 应用
    
    参数:
        activity_name (str): 要打开的应用程序包名
        
    返回:
        bool: 操作是否成功
    """
    try:
        # 使用 am start 命令启动应用的主活动
        cmd = f"adb shell am start -W {activity_name}"
        if output_file == None:
            subprocess.run(cmd, shell=True, check=True)
        elif output_file == subprocess.DEVNULL:
            subprocess.run(cmd, shell=True, check=True,stdout=subprocess.DEVNULL)
        else:
            with open(output_file,'a') as f:
                subprocess.run(cmd, shell=True, check=True, stdout=f)
        print(f"成功打开应用: {activity_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"打开应用失败: {e}")
        return False
    except Exception as e:
        print(f"发生错误: {e}")
        return False


def go_to_home_screen():
    """
    使用 ADB 命令让 Android 设备退回主界面
    """
    try:
        # 发送 HOME 键事件（KEYCODE_HOME = 3）
        cmd = "adb shell input keyevent KEYCODE_HOME"
        subprocess.run(cmd, shell=True, check=True, timeout=10)
        print("已退回主界面")
        return True
    except subprocess.CalledProcessError as e:
        print(f"执行失败: {e}")
        return False
    except subprocess.TimeoutExpired:
        print("命令执行超时")
        return False
    except Exception as e:
        print(f"发生未知错误: {e}")
        return False

def close_app(package_name):
    """
    关闭指定的 Android 应用
    
    参数:
        package_name (str): 要关闭的应用程序包名
        
    返回:
        bool: 操作是否成功
    """
    try:
        # 使用 am force-stop 命令强制停止应用
        cmd = f"adb shell am force-stop {package_name}"
        subprocess.run(cmd, shell=True, check=True)
        cmd = f'adb shell am force-stop com.android.chrome'
        subprocess.run(cmd, shell=True, check=True)
        # print(f"成功关闭应用: {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"关闭应用失败: {e}")
        return False
    except Exception as e:
        print(f"发生错误: {e}")
        return False

def clean_all_apps():
    for package in gb_app_package_list:
        close_app(package)
    for package in mb_app_package_list:
        close_app(package)
    

def pause(sec):
    time.sleep(sec)

                

def clean_file_cache():
    cmd = 'adb shell "su -c \'sync && echo 3 > /proc/sys/vm/drop_caches\'"'
    for i in range(3):
        pause(2)
        subprocess.run(cmd, shell=True, check=True)
        
# def gen_light_load():
#     # TODO

# def gen_medium_load(avoid_app):
#     # TODO

# def gen_high_load(avoid_app):
#     # TODO
    
    
            
if __name__=='__main__':
    for activity in gb_app_activity_list:
        open_app(activity)
    for activity in mb_app_activity_list:
        open_app(activity)
            
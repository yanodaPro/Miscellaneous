import requests
import re
import json
import os
import time
from urllib.parse import urlparse, parse_qs
import subprocess
from typing import Optional, Dict, Any, List
import qrcode
from PIL import Image
import threading

class BilibiliVideoDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com/',
        }
        self.session.headers.update(self.headers)
        self.is_logged_in = False
        self.cookies = None

    def extract_bvid(self, input_str: str) -> Optional[str]:
        """从输入中提取BV号"""
        # 如果是URL
        if input_str.startswith('http'):
            parsed_url = urlparse(input_str)
            path = parsed_url.path
            # 匹配BV号模式
            bv_match = re.search(r'BV[0-9A-Za-z]{10}', path)
            if bv_match:
                return bv_match.group()
            return None
        # 如果是纯BV号
        elif input_str.startswith('BV'):
            return input_str
        else:
            return None

    def get_video_info(self, bvid: str) -> Dict[str, Any]:
        """获取视频信息"""
        api_url = f"https://api.bilibili.com/x/web-interface/view"
        params = {'bvid': bvid}
        
        try:
            response = self.session.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['code'] == 0:
                return data['data']
            else:
                raise Exception(f"获取视频信息失败: {data['message']}")
        except Exception as e:
            raise Exception(f"获取视频信息时出错: {str(e)}")

    def qr_login(self) -> bool:
        """扫码登录B站"""
        try:
            # 获取登录二维码
            qr_url = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
            response = self.session.get(qr_url)
            qr_data = response.json()
            
            if qr_data['code'] != 0:
                print("获取二维码失败")
                return False
            
            qr_code_url = qr_data['data']['url']
            qrcode_key = qr_data['data']['qrcode_key']
            
            # 生成二维码图片
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_code_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img.save("bilibili_qr.png")
            
            print("二维码已生成: bilibili_qr.png")
            print("请使用B站APP扫描二维码登录")
            
            # 显示二维码（如果环境支持）
            try:
                img.show()
            except:
                pass
            
            # 轮询检查登录状态
            return self._check_login_status(qrcode_key)
            
        except Exception as e:
            print(f"登录过程中出错: {str(e)}")
            return False

    def _check_login_status(self, qrcode_key: str) -> bool:
        """检查登录状态"""
        check_url = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
        params = {'qrcode_key': qrcode_key}
        
        for i in range(180):  # 最多等待3分钟
            try:
                response = self.session.get(check_url, params=params)
                status_data = response.json()
                
                if status_data['code'] == 0:
                    data = status_data['data']
                    if data['code'] == 0:  # 登录成功
                        print("登录成功!")
                        self.is_logged_in = True
                        self.cookies = self.session.cookies.get_dict()
                        return True
                    elif data['code'] == 86038:  # 二维码过期
                        print("二维码已过期，请重新运行程序")
                        return False
                    elif data['code'] == 86090:  # 二维码已扫描未确认
                        print("二维码已扫描，请在手机上确认登录")
                else:
                    print(f"检查登录状态失败: {status_data['message']}")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"检查登录状态时出错: {str(e)}")
                time.sleep(1)
        
        print("登录超时")
        return False

    def get_video_play_url(self, bvid: str, cid: str, quality: int = 80) -> Dict[str, Any]:
        """获取视频播放地址"""
        api_url = "https://api.bilibili.com/x/player/playurl"
        params = {
            'bvid': bvid,
            'cid': cid,
            'qn': quality,  # 视频质量
            'fnval': 16,    # 支持dash格式
            'fourk': 1,     # 支持4K
        }
        
        try:
            response = self.session.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['code'] == 0:
                return data['data']
            else:
                raise Exception(f"获取播放地址失败: {data['message']}")
        except Exception as e:
            raise Exception(f"获取播放地址时出错: {str(e)}")

    def download_file(self, url: str, filename: str, file_type: str = "文件") -> bool:
        """下载文件"""
        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"\r下载{file_type}进度: {progress:.1f}%", end='', flush=True)
            
            print(f"\n{file_type}下载完成: {filename}")
            return True
            
        except Exception as e:
            print(f"\n{file_type}下载失败: {str(e)}")
            return False

    def download_cover(self, cover_url: str, filename: str) -> bool:
        """下载封面图片"""
        try:
            print(f"开始下载封面图片: {filename}")
            return self.download_file(cover_url, filename, "封面")
        except Exception as e:
            print(f"下载封面图片失败: {str(e)}")
            return False

    def choose_quality(self, quality_list: list) -> int:
        """选择视频质量"""
        print("\n可选清晰度:")
        quality_map = {
            127: ('8K 超高清', True),
            126: ('4K 杜比视界', True),
            120: ('4K 超清', True),
            116: ('1080P 60帧', True),
            112: ('1080P+ 高码率', True),
            80: ('1080P 高清', True),
            64: ('720P 高清', False),
            32: ('480P 清晰', False),
            16: ('360P 流畅', False)
        }
        
        available_qualities = []
        for qn in quality_list:
            if qn in quality_map:
                name, need_login = quality_map[qn]
                login_status = " (需登录)" if need_login and not self.is_logged_in else ""
                print(f"{qn}: {name}{login_status}")
                available_qualities.append(qn)
        
        while True:
            try:
                choice = int(input("请选择清晰度编号: "))
                if choice in available_qualities:
                    # 检查是否需要登录但未登录
                    if quality_map[choice][1] and not self.is_logged_in:
                        print("此清晰度需要登录才能下载，请先登录")
                        login_choice = input("是否现在登录? (y/n): ").lower()
                        if login_choice == 'y':
                            if self.qr_login():
                                return choice
                            else:
                                print("登录失败，请重新选择清晰度")
                        else:
                            print("请重新选择清晰度")
                    else:
                        return choice
                else:
                    print("无效的选择，请重新输入")
            except ValueError:
                print("请输入有效的数字")

    def choose_download_type(self) -> str:
        """选择下载类型"""
        print("\n请选择下载类型:")
        print("1: 仅视频 (无音频)")
        print("2: 仅音频")
        print("3: 视频+音频 (合并)")
        print("4: 仅封面图片")
        print("5: 视频+音频+封面 (合并视频和音频)")
        
        while True:
            choice = input("请选择下载类型 (1/2/3/4/5): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return choice
            else:
                print("无效的选择，请重新输入")

    def merge_video_audio(self, video_file: str, audio_file: str, output_file: str) -> bool:
        """合并视频和音频文件"""
        try:
            # 检查ffmpeg是否可用
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("未找到ffmpeg，无法自动合并视频和音频")
                print(f"视频文件: {video_file}")
                print(f"音频文件: {audio_file}")
                return False
            
            # 使用ffmpeg合并视频和音频
            cmd = [
                'ffmpeg', '-i', video_file, '-i', audio_file,
                '-c', 'copy',  # 直接复制流，不重新编码
                '-y',  # 覆盖输出文件
                output_file
            ]
            
            print("正在合并视频和音频...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"合并完成: {output_file}")
                # 删除临时文件
                try:
                    os.remove(video_file)
                    os.remove(audio_file)
                    print("临时文件已删除")
                except:
                    print("临时文件删除失败")
                return True
            else:
                print(f"合并失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"合并过程中出错: {str(e)}")
            return False

    def download_video_by_bvid(self, input_str: str, quality: Optional[int] = None, download_type: Optional[str] = None) -> bool:
        """主下载函数"""
        try:
            # 提取BV号
            bvid = self.extract_bvid(input_str)
            if not bvid:
                print("无效的BV号或URL")
                return False
            
            print(f"正在处理视频: {bvid}")
            
            # 获取视频信息
            video_info = self.get_video_info(bvid)
            title = video_info['title']
            cid = video_info['cid']
            cover_url = video_info['pic']  # 封面图片URL
            
            print(f"视频标题: {title}")
            print(f"视频CID: {cid}")
            print(f"封面URL: {cover_url}")
            
            # 选择下载类型
            if not download_type:
                download_type = self.choose_download_type()
            
            # 清理文件名
            safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
            
            # 仅下载封面图片
            if download_type == '4':
                cover_filename = f"{safe_title}_{bvid}_cover.jpg"
                return self.download_cover(cover_url, cover_filename)
            
            # 获取播放信息
            play_info = self.get_video_play_url(bvid, cid)
            
            # 选择清晰度
            if not quality:
                accept_quality = play_info.get('accept_quality', [])
                quality = self.choose_quality(accept_quality)
            
            # 重新获取指定清晰度的播放信息
            play_info = self.get_video_play_url(bvid, cid, quality)
            
            # 获取视频和音频URL（优先使用dash格式）
            video_url = None
            audio_url = None
            
            if 'dash' in play_info:
                # 使用dash视频流
                video_streams = play_info['dash']['video']
                audio_streams = play_info['dash']['audio']
                
                if video_streams:
                    # 选择第一个视频流（通常是最高质量的）
                    video_url = video_streams[0]['baseUrl']
                    print(f"视频流URL获取成功")
                    
                if audio_streams:
                    # 选择第一个音频流
                    audio_url = audio_streams[0]['baseUrl']
                    print(f"音频流URL获取成功")
            else:
                # 回退到普通格式（仅视频，包含音频）
                durl = play_info['durl']
                if durl:
                    video_url = durl[0]['url']
                    print("注意: 此视频格式不支持单独下载音频")
            
            # 根据下载类型执行下载
            if download_type == '1':  # 仅视频
                if not video_url:
                    print("无法获取视频URL")
                    return False
                
                filename = f"{safe_title}_{bvid}_video.mp4"
                print(f"开始下载视频: {filename}")
                return self.download_file(video_url, filename, "视频")
                
            elif download_type == '2':  # 仅音频
                if not audio_url:
                    print("无法获取音频URL")
                    return False
                
                filename = f"{safe_title}_{bvid}_audio.m4a"
                print(f"开始下载音频: {filename}")
                return self.download_file(audio_url, filename, "音频")
                
            elif download_type == '3':  # 视频+音频
                if not video_url:
                    print("无法获取视频URL")
                    return False
                if not audio_url:
                    print("无法获取音频URL，将只下载视频")
                    filename = f"{safe_title}_{bvid}.mp4"
                    return self.download_file(video_url, filename, "视频")
                
                # 下载视频和音频
                video_filename = f"{safe_title}_{bvid}_video_temp.mp4"
                audio_filename = f"{safe_title}_{bvid}_audio_temp.m4a"
                output_filename = f"{safe_title}_{bvid}.mp4"
                
                print("开始下载视频部分...")
                video_success = self.download_file(video_url, video_filename, "视频")
                
                print("开始下载音频部分...")
                audio_success = self.download_file(audio_url, audio_filename, "音频")
                
                if video_success and audio_success:
                    print("开始合并视频和音频...")
                    return self.merge_video_audio(video_filename, audio_filename, output_filename)
                else:
                    print("视频或音频下载失败，无法合并")
                    return False
            
            elif download_type == '5':  # 视频+音频+封面
                # 首先下载封面
                cover_filename = f"{safe_title}_{bvid}_cover.jpg"
                cover_success = self.download_cover(cover_url, cover_filename)
                
                if not cover_success:
                    print("封面下载失败，继续下载视频和音频")
                
                # 然后下载视频和音频
                if not video_url:
                    print("无法获取视频URL")
                    return False
                if not audio_url:
                    print("无法获取音频URL，将只下载视频")
                    filename = f"{safe_title}_{bvid}.mp4"
                    return self.download_file(video_url, filename, "视频")
                
                # 下载视频和音频
                video_filename = f"{safe_title}_{bvid}_video_temp.mp4"
                audio_filename = f"{safe_title}_{bvid}_audio_temp.m4a"
                output_filename = f"{safe_title}_{bvid}.mp4"
                
                print("开始下载视频部分...")
                video_success = self.download_file(video_url, video_filename, "视频")
                
                print("开始下载音频部分...")
                audio_success = self.download_file(audio_url, audio_filename, "音频")
                
                if video_success and audio_success:
                    print("开始合并视频和音频...")
                    return self.merge_video_audio(video_filename, audio_filename, output_filename)
                else:
                    print("视频或音频下载失败，无法合并")
                    return False
            
        except Exception as e:
            print(f"下载过程中出错: {str(e)}")
            return False

    def set_progress_callback(self, callback):
        """设置进度回调函数"""
        self.progress_callback = callback

    def _download_with_progress(self, url, filename):
        """带进度显示的下载方法"""
        if self.progress_callback:
            # 使用支持进度的下载方式
            response = requests.get(url, stream=True, headers=self.headers)
            total_size = int(response.headers.get('content-length', 0))

            downloaded = 0
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        self.progress_callback(filename, downloaded, total_size)
            return True
        else:
            # 使用原来的下载方式
            return self._download_file(url, filename)

def main():
    downloader = BilibiliVideoDownloader()
    
    print("=" * 50)
    print("B站视频下载器")
    print("=" * 50)
    
    # 询问是否登录
    login_choice = input("是否扫码登录以获取高清视频? (y/n): ").lower()
    if login_choice == 'y':
        if downloader.qr_login():
            print("登录状态: 已登录")
        else:
            print("登录状态: 未登录")
    else:
        print("登录状态: 未登录")
    
    while True:
        print("\n" + "=" * 30)
        input_str = input("请输入BV号或视频URL (输入 'quit' 退出): ").strip()
        
        if input_str.lower() == 'quit':
            break
        
        if not input_str:
            continue
        
        # 开始下载
        success = downloader.download_video_by_bvid(input_str)
        
        if success:
            print("下载成功!")
        else:
            print("下载失败!")
        
        time.sleep(1)

if __name__ == "__main__":
    main()
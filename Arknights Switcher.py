import os
import shutil
import json
import sys

# ================= 🔧 配置区域 (已修改适配 EXE) =================
# 1. 智能获取程序所在的基础目录
if getattr(sys, 'frozen', False):
    # 如果是打包后的 exe，使用 exe 所在目录
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 如果是 python 脚本，使用脚本所在目录
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 配置文件路径 (强制在 exe 同级)
CONFIG_FILE = os.path.join(BASE_DIR, 'switcher_config.json')

# 3. 补丁文件夹名称 (只是名字，后面拼接)
DIR_NAME_BILI = 'bilibili_diff'
DIR_NAME_OFFICIAL = 'official_diff'

# 4. 差异文件内部包裹的目录名
INNER_DIR_NAME = 'Arknights Game'

# 5. 游戏原本的相对路径结构
GAME_SUB_PATH = os.path.join('games', 'Arknights Game')
# ============================================================

def load_config():
    """读取配置文件"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(path):
    """保存路径配置"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({'game_root': path}, f, indent=4, ensure_ascii=False)
        print("💾 路径配置已保存。")
    except Exception as e:
        print(f"⚠️ 配置保存失败: {e}")

def resolve_target_path(user_input):
    """
    解析用户输入的路径，目标是找到 .../Arknights Game
    """
    path = os.path.abspath(user_input.strip().strip('"').strip("'"))
    
    # 情况A: 用户输入的是 .../Arknights Game
    if os.path.basename(path) == 'Arknights Game':
        if os.path.exists(path):
            return path
            
    # 情况B: 用户输入的是启动器目录 (例如 .../Arknights bilibili)
    # 我们尝试拼接 games/Arknights Game
    potential_path = os.path.join(path, GAME_SUB_PATH)
    if os.path.exists(potential_path):
        return potential_path
        
    return path # 如果都找不到，就返回原样，让后面报错

def overwrite_files(source_root, target_root):
    """
    核心覆盖逻辑
    """
    if not os.path.exists(source_root):
        print(f"\n❌ 错误：找不到源文件夹 [{source_root}]")
        print(f"   请检查 [{os.path.basename(os.path.dirname(source_root))}] 文件夹是否在 EXE 同级目录下。")
        return

    print(f"\n📂 正在准备覆盖...")
    print(f"   源: {source_root}")
    print(f"   至: {target_root}")
    
    # 使用 copytree 进行覆盖 (Python 3.8+ 支持 dirs_exist_ok=True)
    try:
        shutil.copytree(source_root, target_root, dirs_exist_ok=True)
        print("\n✅ 覆盖完成！")
    except Exception as e:
        print(f"\n❌ 覆盖过程中发生错误: {e}")

def main():
    print("==========================================")
    print("      🔄 明日方舟 官服/B服 切换工具")
    print("==========================================")
    print(f"📂 工作目录: {BASE_DIR}")  # 方便调试看到底在哪

    # --- 1. 读取/询问路径 ---
    config = load_config()
    saved_path = config.get('game_root', '')
    final_path = ''

    if saved_path:
        print(f"📍 发现上次使用的路径: {saved_path}")
        # 验证这个路径是否还能解析出有效的游戏目录
        real_game_dir = resolve_target_path(saved_path)
        
        if os.path.exists(real_game_dir):
            if input("   直接使用此路径？(回车确认，输入n重新设定): ").lower() != 'n':
                final_path = real_game_dir
        else:
            print("⚠️ 上次的路径似乎已失效。")

    if not final_path:
        print("\n请输入游戏目录 (支持粘贴启动器目录或游戏本体目录):")
        user_input = input("👉 路径: ")
        final_path = resolve_target_path(user_input)
        
        if not os.path.exists(final_path):
            print("❌ 错误：无法定位到 'Arknights Game' 文件夹，请检查路径。")
            input("按回车键退出...")
            return
        
        # 保存用户原始输入的路径（方便下次识别）
        save_config(user_input)

    print(f"\n✅ 目标锁定: {final_path}")

    # --- 2. 询问操作 ---
    print("\n请选择切换方向：")
    print(" [1] 变成 -> Bilibili 服 (写入B服文件)")
    print(" [2] 变成 -> 官方服 (写入官服文件)")
    
    choice = input("\n👉 请输入 (1/2): ").strip()

    # --- 3. 执行 ---
    # 构建源文件路径：使用全局计算好的 BASE_DIR
    
    if choice == '1':
        # 目标是B服，源文件选 bilibili_diff/Arknights Game
        source_dir = os.path.join(BASE_DIR, DIR_NAME_BILI, INNER_DIR_NAME)
        print("\n🚀 正在切换为 [Bilibili服] ...")
        overwrite_files(source_dir, final_path)
        
    elif choice == '2':
        # 目标是官服，源文件选 official_diff/Arknights Game
        source_dir = os.path.join(BASE_DIR, DIR_NAME_OFFICIAL, INNER_DIR_NAME)
        print("\n🚀 正在切换为 [官方服] ...")
        overwrite_files(source_dir, final_path)
        
    else:
        print("❌ 无效选项。")

    input("\n按回车键退出...")

if __name__ == "__main__":
    main()

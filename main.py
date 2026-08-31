# ====== 统一入口：让程序从 main.py 启动 ======
from agent import CustomerServiceAgent

if __name__ == "__main__":
    agent = CustomerServiceAgent()
    agent.run()
"""
收盘总结深度分析报告
使用通达信 tqcenter 接口获取数据，生成全面的市场收盘分析
"""

import sys, os, winreg
from datetime import datetime
from contextlib import contextmanager
import io


@contextmanager
def silence_stdout():
    old = sys.stdout
    sys.stdout = io.StringIO()
    try:
        yield
    finally:
        sys.stdout = old

key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\通达信金融终端64"
with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
    tdx_root, _ = winreg.QueryValueEx(key, "InstallLocation")

sys.path.insert(0, os.path.join(tdx_root, 'PYPlugins', 'user'))
from tqcenter import tq

with silence_stdout():
    tq.initialize(__file__)


def silent_get_snapshot(code):
    with silence_stdout():
        try:
            snap = tq.get_market_snapshot(code)
            if snap and snap.get('ErrorId') == '0':
                return snap
        except Exception:
            pass
    return None


def silent_get_stock_info(code, fields):
    with silence_stdout():
        try:
            return tq.get_stock_info(code, field_list=fields)
        except Exception:
            pass
    return {}


class ClosingReport:

    INDEX_MAP = {
        '000001.SH': '上证指数', '399001.SZ': '深证成指',
        '399006.SZ': '创业板指', '000688.SH': '科创50',
        '000300.SH': '沪深300', '000016.SH': '上证50',
        '000905.SH': '中证500', '000852.SH': '中证1000',
        '880001.SH': '全A指数',
    }

    def __init__(self):
        self.today = datetime.now()
        self.report_data = {}
        self.sector_codes = self._load_sectors()

    def _load_sectors(self):
        """动态加载研究行业3级分类板块列表"""
        with silence_stdout():
            try:
                sectors = tq.get_stock_list(market='18', list_type=1)
                if sectors:
                    return [s['Code'] for s in sectors if s.get('Code')]
            except Exception:
                pass
        return []

    def get_index_data(self):
        codes = list(self.INDEX_MAP.keys())
        snapshots = {}
        for code in codes:
            snap = silent_get_snapshot(code)
            if snap:
                snapshots[code] = snap

        self.report_data['index'] = {}
        for code in codes:
            name = self.INDEX_MAP[code]
            snap = snapshots.get(code)
            if not snap:
                continue
            lc = float(snap.get('LastClose', 0))
            now = float(snap.get('Now', 0))
            change = now - lc
            change_pct = (change / lc * 100) if lc else 0
            amp = ((float(snap.get('Max', 0)) - float(snap.get('Min', 0))) / lc * 100) if lc else 0
            self.report_data['index'][code] = {
                'name': name, 'close': now,
                'open': float(snap.get('Open', 0)),
                'high': float(snap.get('Max', 0)),
                'low': float(snap.get('Min', 0)),
                'pre_close': lc, 'change': round(change, 2),
                'change_pct': round(change_pct, 2),
                'amplitude': round(amp, 2),
                'volume': float(snap.get('Volume', 0)),
                'amount': float(snap.get('Amount', 0)),
            }
        return self.report_data['index']

    def get_market_overview(self):
        """从全A指数快照获取涨跌家数等市场全局数据"""
        snap_all = silent_get_snapshot('880001.SH')
        data = {}
        if snap_all:
            data['up_count'] = snap_all.get('UpHome', 'N/A')
            data['down_count'] = snap_all.get('DownHome', 'N/A')
            data['zt_count'] = snap_all.get('Outside', 'N/A')
            data['dt_count'] = snap_all.get('Inside', 'N/A')

        with silence_stdout():
            try:
                sc = tq.get_scjy_value(field_list=['SC01', 'SC02', 'SC33', 'SC39', 'SC28'])
                if sc:
                    for fld in sc:
                        recs = sc[fld]
                        if recs:
                            vals = recs[-1].get('Value', [])
                            data[fld] = vals
            except Exception:
                pass

        self.report_data['market'] = data
        return data

    def get_sector_performance(self):
        sector_data = []
        for code in self.sector_codes:
            snap = silent_get_snapshot(code)
            if not snap:
                continue
            lc = float(snap.get('LastClose', 0))
            now = float(snap.get('Now', 0))
            pct = round((now - lc) / lc * 100, 2) if lc else 0
            info = silent_get_stock_info(code, ['Name'])
            name = info.get('Name', code) if info else code
            sector_data.append({
                'code': code, 'name': name, 'close': now,
                'change_pct': pct, 'volume': float(snap.get('Volume', 0)),
                'amount': float(snap.get('Amount', 0)),
            })

        sector_data.sort(key=lambda x: x['change_pct'], reverse=True)
        self.report_data['sectors'] = sector_data
        return sector_data

    def generate_report(self):
        print('=' * 70)
        print(f'  收盘总结深度分析报告')
        print(f'  {self.today.strftime("%Y年%m月%d日 %A")}')
        print('=' * 70)

        # 一、主要指数表现
        print('\n【一、主要指数表现】')
        print('-' * 70)
        print(f'{"指数":<12}{"收盘价":>10}{"涨跌幅":>10}{"涨幅":>10}{"振幅":>10}{"成交额(亿)":>12}')
        print('-' * 70)
        index_data = self.get_index_data()
        if index_data:
            for idx in sorted(index_data.values(), key=lambda x: x['change_pct'], reverse=True):
                cs = f"+{idx['change_pct']}%" if idx['change_pct'] >= 0 else f"{idx['change_pct']}%"
                ay = idx['amount'] / 10000 if idx['amount'] else 0
                print(f'{idx["name"]:<12}{idx["close"]:>10.2f}{cs:>10}{idx["change"]:>10.2f}{idx["amplitude"]:>10.2f}{ay:>12.2f}')

        # 二、市场整体概况
        print('\n【二、市场整体概况】')
        print('-' * 40)
        market = self.get_market_overview()

        up = market.get('up_count', 'N/A')
        down = market.get('down_count', 'N/A')
        zt = market.get('zt_count', 'N/A')
        dt = market.get('dt_count', 'N/A')
        print(f'  上涨家数: {str(up):>6}    下跌家数: {str(down):>6}')
        print(f'  涨停家数: {str(zt):>6}    跌停家数: {str(dt):>6}')

        sc39 = market.get('SC39', [])
        if sc39:
            print(f'  涨幅>=5%: {sc39[0]:>6}    跌幅>=5%: {sc39[1]:>6}')

        sc28 = market.get('SC28', [])
        if sc28:
            print(f'  历史新高: {sc28[0]:>6}    历史新低: {sc28[1]:>6}')

        total_amt = sum(d['amount'] for d in index_data.values()) if index_data else 0
        print(f'  主要指数总成交额: {total_amt / 10000:.2f} 亿')

        sc02 = market.get('SC02', [])
        if len(sc02) >= 2:
            sh_f = float(sc02[0]) if sc02[0] else 0
            sz_f = float(sc02[1]) if sc02[1] else 0
            total_f = sh_f + sz_f
            fs = f'+{total_f:.2f}亿' if total_f >= 0 else f'{total_f:.2f}亿'
            print(f'  北向资金净流入: {fs} (沪股通:{sh_f:.2f}亿 深股通:{sz_f:.2f}亿)')

        sc01 = market.get('SC01', [])
        if len(sc01) >= 2:
            print(f'  融资余额: {float(sc01[0]) / 10000:.2f}亿    融券余额: {float(sc01[1]) / 10000:.2f}亿')

        # 三、行业板块排名
        print('\n【三、行业板块涨跌幅排名】')
        print('-' * 70)
        print(f'{"板块名称":<16}{"收盘价":>10}{"涨跌幅":>10}{"成交额(亿)":>12}')
        print('-' * 50)
        sector_data = self.get_sector_performance()
        if sector_data:
            print(f'  -- 涨幅前10 --')
            for s in sector_data[:10]:
                pct = f"+{s['change_pct']}%" if s['change_pct'] >= 0 else f"{s['change_pct']}%"
                amt = s['amount'] / 10000 if s['amount'] else 0
                print(f'  {s["name"]:<14}{s["close"]:>10.2f}{pct:>10}{amt:>12.2f}')
            print(f'  -- 跌幅前10 --')
            for s in sector_data[-10:]:
                pct = f"+{s['change_pct']}%" if s['change_pct'] >= 0 else f"{s['change_pct']}%"
                amt = s['amount'] / 10000 if s['amount'] else 0
                print(f'  {s["name"]:<14}{s["close"]:>10.2f}{pct:>10}{amt:>12.2f}')

        # 四、市场情绪指标
        print('\n【四、市场情绪指标】')
        print('-' * 40)
        sc33 = market.get('SC33', [])
        if sc33:
            print(f'  涨停封单金额: {sc33[0]}亿    跌停封单金额: {sc33[1]}亿')

        # 五、市场总结
        print('\n【五、市场总结】')
        print('-' * 40)
        if index_data:
            sh = index_data.get('000001.SH', {})
            if sh:
                pct = sh['change_pct']
                if pct >= 2: trend = '强势上涨'
                elif pct >= 0.5: trend = '震荡偏强'
                elif pct >= -0.5: trend = '窄幅震荡'
                elif pct >= -2: trend = '震荡偏弱'
                else: trend = '弱势下跌'

                try:
                    uc = int(float(up)) if up != 'N/A' else 0
                    dc = int(float(down)) if down != 'N/A' else 0
                    ztc = int(float(zt)) if zt != 'N/A' else 0
                except:
                    uc, dc, ztc = 0, 0, 0

                if uc > dc * 1.5 and ztc > 50: sentiment = '市场情绪高涨'
                elif uc > dc: sentiment = '市场情绪偏暖'
                elif dc > uc: sentiment = '市场情绪偏冷'
                else: sentiment = '市场情绪中性'

                direction = '上涨' if sh['change'] >= 0 else '下跌'
                print(f'  今日大盘{trend}，{sentiment}。')
                print(f'  上证指数收于 {sh["close"]:.2f} 点，{direction}{abs(sh["change"]):.2f}点，涨幅 {sh["change_pct"]:.2f}%。')
                print(f'  市场涨跌互现，上涨{uc}家，下跌{dc}家，涨停{ztc}家。')

        print('\n' + '=' * 70)
        print(f'  报告生成完毕  {self.today.strftime("%Y-%m-%d %H:%M:%S")}')
        print('=' * 70)

    def save_report(self, filepath=None):
        if filepath is None:
            filepath = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                f'收盘总结_{self.today.strftime("%Y%m%d")}.txt'
            )
        original = sys.stdout
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                sys.stdout = f
                self.generate_report()
        finally:
            sys.stdout = original
        print(f'\n报告已保存至: {filepath}')
        return filepath

    def close(self):
        tq.close()


def main():
    report = ClosingReport()
    try:
        report.generate_report()
        report.save_report()
    except Exception as e:
        print(f'\n错误: {e}')
        import traceback
        traceback.print_exc()
    finally:
        report.close()


if __name__ == '__main__':
    main()

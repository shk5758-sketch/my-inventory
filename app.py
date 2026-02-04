from flask import Flask, render_template_string, request
from datetime import datetime

app = Flask(__name__)

# [데이터 로직] 실제로는 여기서 엑셀 파일을 읽어 날짜별 데이터를 반환하게 됩니다.
def get_inventory_data(selected_date):
    # 엑셀 매칭을 위한 데이터 구조 예시
    data = {}
    for s in ['A', 'B']:
        for r_val in [100, 200, 300, 400, 500]:
            for c in range(1, 15):
                pos = f"{s}{r_val + c:02d}"
                # 엑셀에서 이 pos(예: A101)를 찾아 데이터를 매칭하게 됩니다.
                data[pos] = {"t": "대기중", "v": "-", "c": "gray"}
    
    # 예시: 특정 날짜에 데이터가 있는 경우 (나중에 엑셀 연동 시 이 부분이 동적으로 바뀜)
    if selected_date:
        data["A101"] = {"t": "WASW", "v": "1,508", "c": "blue"}
        data["A201"] = {"t": "WCRS", "v": "1,671", "c": "orange"}
        data["B101"] = {"t": "YBG2", "v": "2,308", "c": "green"}
        
    return data

html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>일일재고현황표</title>
    <style>
        body { font-family: 'Malgun Gothic'; background: #f0f2f5; margin: 0; padding: 20px; min-width: 1800px; }
        
        /* 상단 헤더 및 날짜 선택기 레이아웃 */
        .top-bar { display: flex; justify-content: space-between; align-items: center; padding: 10px 50px; margin-bottom: 20px; }
        .header-title { flex-grow: 1; text-align: center; }
        .title { font-size: 45px; font-weight: bold; text-decoration: underline; letter-spacing: 15px; margin-left: 200px; }
        
        .date-picker-container { background: white; padding: 15px 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #ddd; }
        .date-picker-container label { font-weight: bold; margin-right: 10px; color: #333; }
        .date-input { padding: 8px; font-size: 16px; border-radius: 5px; border: 1px solid #ccc; cursor: pointer; }
        .btn-search { padding: 8px 15px; background: #333; color: white; border: none; border-radius: 5px; cursor: pointer; margin-left: 10px; }
        .btn-search:hover { background: #555; }

        .silo-wrapper { background: white; padding: 60px 20px; border-radius: 15px; margin-bottom: 60px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); clear: both; }
        .section-title { text-align: center; font-size: 32px; font-weight: bold; margin-bottom: 50px; }

        .grid-container { display: flex; justify-content: center; gap: 120px; }
        table { border-collapse: collapse; margin-top: 50px; } 
        td { width: 105px; height: 160px; border: 1.5px solid #333; position: relative; background: #fff; padding: 0; }

        .circle { 
            width: 100px; height: 100px; border: 2.5px solid black; border-radius: 50%; 
            display: flex; flex-direction: column; justify-content: center; align-items: center; 
            background: white; position: absolute; right: -52px; bottom: -52px; z-index: 10;
            box-shadow: 3px 3px 8px rgba(0,0,0,0.2);
        }
        .circle.pos-top { top: -52px; bottom: auto; }

        .box-content { display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%; }
        .t { font-size: 13px; font-weight: 900; }
        .v { font-size: 18px; font-weight: 900; margin: 2px 0; }
        .p { font-size: 10px; font-weight: bold; color: #444; background: #eee; padding: 1px 3px; border-radius: 3px; }

        .blue { color: #0055ff; } .orange { color: #e67e22; } .green { color: #27ae60; } .red { color: #ff0000; } .gray { color: #bbb; }
    </style>
</head>
<body>
    <div class="top-bar">
        <div class="header-title">
            <div class="title">일 일 재 고 현 황 표</div>
        </div>
        <div class="date-picker-container">
            <form action="/" method="get">
                <label for="date">조회 일자:</label>
                <input type="date" id="date" name="date" class="date-input" value="{{ selected_date }}">
                <button type="submit" class="btn-search">조회</button>
            </form>
        </div>
    </div>

    {% for s_type in ['A', 'B'] %}
    <div class="silo-wrapper">
        <div class="section-title">싸이로 {{ s_type }} 구역 현황</div>
        <div class="grid-container">
            {% for start_col, end_col in [(1, 8), (8, 15)] %}
            <table>
                {% for r_val in [200, 400] %}
                <tr>
                    {% for c in range(start_col, end_col) %}
                    <td>
                        <div class="box-content {{ d[s_type ~ (r_val + c)].c }}">
                            <div class="t">{{ d[s_type ~ (r_val + c)].t }}</div>
                            <div class="v">{{ d[s_type ~ (r_val + c)].v }}</div>
                            <div class="p">{{ s_type }}{{ r_val + c }}</div>
                        </div>

                        {% if (start_col == 1 and c <= 6) or (start_col == 8 and c <= 13) %}
                            {% if r_val == 200 %}
                            <div class="circle pos-top {{ d[s_type ~ (100 + c)].c }}">
                                <div class="t">{{ d[s_type ~ (100 + c)].t }}</div>
                                <div class="v">{{ d[s_type ~ (100 + c)].v }}</div>
                                <div class="p">{{ s_type }}{{ 100 + c }}</div>
                            </div>
                            <div class="circle {{ d[s_type ~ (300 + c)].c }}">
                                <div class="t">{{ d[s_type ~ (300 + c)].t }}</div>
                                <div class="v">{{ d[s_type ~ (300 + c)].v }}</div>
                                <div class="p">{{ s_type }}{{ 300 + c }}</div>
                            </div>
                            {% endif %}
                            {% if r_val == 400 %}
                            <div class="circle {{ d[s_type ~ (500 + c)].c }}">
                                <div class="t">{{ d[s_type ~ (500 + c)].t }}</div>
                                <div class="v">{{ d[s_type ~ (500 + c)].v }}</div>
                                <div class="p">{{ s_type }}{{ 500 + c }}</div>
                            </div>
                            {% endif %}
                        {% endif %}
                    </td>
                    {% endfor %}
                </tr>
                {% endfor %}
            </table>
            {% endfor %}
        </div>
    </div>
    {% endfor %}
</body>
</html>
"""

@app.route('/')
def index():
    # URL에서 선택된 날짜를 가져옵니다. 없으면 오늘 날짜를 기본값으로 합니다.
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    inventory_data = get_inventory_data(selected_date)
    return render_template_string(html_code, d=inventory_data, selected_date=selected_date)

if __name__ == '__main__':
    app.run(debug=True)
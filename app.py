from flask import Flask, render_template
import pandas as pd
import os

app = Flask(__name__)

# 1. 엑셀 파일 경로 설정 (GitHub에 올리신 파일명과 일치시켰습니다)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE_PATH = os.path.join(BASE_DIR, '20260201.xlsx')

@app.route('/')
def index():
    try:
        # 엑셀 파일이 있는지 확인
        if os.path.exists(EXCEL_FILE_PATH):
            # 2. 데이터 읽기
            df = pd.read_excel(EXCEL_FILE_PATH)
            
            # 3. 사각형 카드용 요약 데이터 계산
            stats = {
                'total_items': len(df),
                'total_qty': int(df['재고수량'].sum()) if '재고수량' in df.columns else 0,
                'low_stock': len(df[df['재고수량'] < 10]) if '재고수량' in df.columns else 0
            }

            # 4. 원형 차트용 데이터 계산 (카테고리별 수량 합계)
            if '카테고리' in df.columns and '재고수량' in df.columns:
                cat_data = df.groupby('카테고리')['재고수량'].sum().to_dict()
                labels = list(cat_data.keys())
                values = list(cat_data.values())
            else:
                labels, values = ["데이터 없음"], [0]

            # 5. 테이블 HTML 변환 (부트스트랩 스타일 적용)
            table_html = df.to_html(classes='table table-hover', index=False)
            
            # 디자인 파일(index.html)로 데이터 전달
            return render_template('index.html', stats=stats, labels=labels, values=values, table=table_html)
        
        else:
            return f"<h1>파일을 찾을 수 없습니다: {EXCEL_FILE_PATH}</h1>"
            
    except Exception as e:
        return f"<h1>에러 발생: {str(e)}</h1><p>엑셀 파일의 컬럼명(품목명, 카테고리, 재고수량)을 확인하세요.</p>"

if __name__ == '__main__':
    # AWS 외부 접속 허용을 위한 설정
    app.run(host='0.0.0.0', port=5000, debug=True)

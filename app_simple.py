import streamlit as st
import pandas as pd
import numpy as np
from simple_auth import SimpleUserManager, login_user, logout_user, register_form

# 사용자 관리자 생성
user_manager = SimpleUserManager()

# 앱 제목 설정
st.title('배당 손익 계산기')

# 인증 관련 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'name' not in st.session_state:
    st.session_state.name = None

# 로그인 섹션
if not st.session_state.authenticated:
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    
    with tab1:
        st.subheader('로그인')
        login_successful = login_user(user_manager)
        
        if login_successful:
            st.rerun()
    
    with tab2:
        st.subheader('회원가입')
        register_form(user_manager)

# 로그인 성공 시 앱 메인 화면
else:
    st.write(f'{st.session_state.name}님 환영합니다!')
    
    # 로그아웃 버튼
    if st.button('로그아웃'):
        logout_user()
        st.rerun()
    
    st.write('종목별 투자 정보와 월별 배당금을 입력하여 손익을 계산해보세요.')
    
    # 세션 상태 초기화
    if 'stocks' not in st.session_state:
        # 사용자의 저장된 종목 정보 로드
        st.session_state.stocks = user_manager.get_user_stocks(st.session_state.username)
    
    # 메뉴 탭 추가
    tab1, tab2, tab3 = st.tabs(["📊 대시보드", "➕ 종목 관리", "📋 상세 정보"])
    
    # 새로운 대시보드 탭
    with tab1:
        if not st.session_state.stocks:
            st.info('종목을 추가하면 여기에 대시보드가 표시됩니다.')
        else:
            st.subheader('포트폴리오 요약')
            
            # 포트폴리오 요약 계산
            total_investment = sum(stock['총 투자금'] for stock in st.session_state.stocks)
            total_current_value = sum(stock['현재 평가금'] for stock in st.session_state.stocks)
            total_dividend = sum(stock['누적 배당금'] for stock in st.session_state.stocks)
            total_profit_loss = sum(stock['실제 손익'] for stock in st.session_state.stocks)
            total_profit_rate = (total_profit_loss / total_investment * 100) if total_investment > 0 else 0
            
            # 주요 지표 표시 (표 형태로)
            st.markdown("### 📈 주요 지표")
            
            summary_data = {
                '항목': ['총 투자금', '총 평가금', '총 배당금', '총 손익', '총 수익률'],
                '금액': [
                    f"{total_investment:,.2f}원",
                    f"{total_current_value:,.2f}원",
                    f"{total_dividend:,.2f}원",
                    f"{total_profit_loss:,.2f}원",
                    f"{total_profit_rate:,.2f}%"
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            st.table(summary_df)
            
            st.markdown("---")
            
            # 종목별 수익률 비교 (표 형태로)
            st.markdown("### 📊 종목별 수익률 비교")
            
            profit_data = []
            for stock in st.session_state.stocks:
                profit_data.append({
                    '종목명': stock['종목명'],
                    '투자금': f"{stock['총 투자금']:,.2f}원",
                    '평가금': f"{stock['현재 평가금']:,.2f}원",
                    '배당금': f"{stock['누적 배당금']:,.2f}원",
                    '수익/손실': f"{stock['실제 손익']:,.2f}원",
                    '수익률': f"{stock['수익률 (%)']:,.2f}%"
                })
            
            profit_df = pd.DataFrame(profit_data)
            # 수익률 기준으로 내림차순 정렬
            profit_df['수익률_정렬용'] = [stock['수익률 (%)'] for stock in st.session_state.stocks]
            profit_df = profit_df.sort_values('수익률_정렬용', ascending=False).drop('수익률_정렬용', axis=1)
            st.table(profit_df)
            
            st.markdown("---")
            
            # 포트폴리오 구성 비중 (표 형태로)
            st.markdown("### 🥧 포트폴리오 구성 비중")
            
            # 투자금 및 평가금 기준 비중 데이터 준비
            composition_data = []
            for stock in st.session_state.stocks:
                invest_pct = (stock['총 투자금'] / total_investment * 100) if total_investment > 0 else 0
                value_pct = (stock['현재 평가금'] / total_current_value * 100) if total_current_value > 0 else 0
                
                composition_data.append({
                    '종목명': stock['종목명'],
                    '투자금': f"{stock['총 투자금']:,.2f}원",
                    '투자 비중': f"{invest_pct:.2f}%",
                    '평가금': f"{stock['현재 평가금']:,.2f}원",
                    '평가 비중': f"{value_pct:.2f}%"
                })
            
            composition_df = pd.DataFrame(composition_data)
            # 투자 비중 기준으로 내림차순 정렬
            composition_df['투자비중_정렬용'] = [(stock['총 투자금'] / total_investment * 100) if total_investment > 0 else 0 
                                        for stock in st.session_state.stocks]
            composition_df = composition_df.sort_values('투자비중_정렬용', ascending=False).drop('투자비중_정렬용', axis=1)
            st.table(composition_df)
            
            st.markdown("---")
            
            # 월별 배당금 현황 (표 형태로)
            st.markdown("### 💰 월별 배당금 현황")
            
            # 모든 종목의 월별 배당금 합산
            monthly_sums = {month: 0 for month in ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']}
            
            for stock in st.session_state.stocks:
                for month, amount in stock['월별 배당금'].items():
                    monthly_sums[month] += amount
            
            monthly_data = {
                '월': list(monthly_sums.keys()),
                '배당금': [f"{amount:,.2f}원" for amount in monthly_sums.values()]
            }
            monthly_df = pd.DataFrame(monthly_data)
            
            # 배당금이 있는 월만 표시
            monthly_df['배당금_정렬용'] = list(monthly_sums.values())
            monthly_df_filtered = monthly_df[monthly_df['배당금_정렬용'] > 0].drop('배당금_정렬용', axis=1)
            
            if not monthly_df_filtered.empty:
                st.table(monthly_df_filtered)
                
                # 배당금 흐름 요약 텍스트
                max_month = monthly_df.loc[monthly_df['배당금_정렬용'].idxmax(), '월']
                max_amount = monthly_df['배당금_정렬용'].max()
                annual_dividend = sum(monthly_sums.values())
                
                st.markdown(f"**배당금 요약:**")
                st.markdown(f"- 연간 총 배당금: **{annual_dividend:,.2f}원**")
                st.markdown(f"- 배당금이 가장 많은 달: **{max_month}** ({max_amount:,.2f}원)")
                st.markdown(f"- 월 평균 배당금: **{(annual_dividend/12):,.2f}원**")
            else:
                st.info("아직 입력된 배당금이 없습니다.")
    
    # 종목 관리 탭   
    with tab2:
        # 종목 추가 폼
        with st.form('add_stock_form'):
            st.subheader('종목 정보 입력')
            col1, col2 = st.columns(2)
            
            with col1:
                stock_name = st.text_input('종목명', placeholder='예: 리얼티인컴')
                quantity = st.number_input('보유 수량', min_value=0, value=0, step=1)
                purchase_price = st.number_input('매수 단가', min_value=0.0, value=0.0, step=0.01)
            
            with col2:
                current_price = st.number_input('현재 주가', min_value=0.0, value=0.0, step=0.01)
            
            st.subheader('월별 배당금')
            
            # 한 줄에 4개 열로 배치
            col1, col2, col3, col4 = st.columns(4)
            
            monthly_dividends = {}
            months = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
            
            for i, month in enumerate(months):
                with [col1, col2, col3, col4][i % 4]:
                    monthly_dividends[month] = st.number_input(
                        month, 
                        min_value=0.0,
                        value=0.0,
                        step=0.01,
                        key=f"dividend_{month}"
                    )
            
            submit_button = st.form_submit_button('종목 추가')
            
            if submit_button:
                if not stock_name:
                    st.error('종목명을 입력해주세요.')
                elif quantity <= 0:
                    st.error('보유 수량은 0보다 커야 합니다.')
                elif purchase_price <= 0:
                    st.error('매수 단가는 0보다 커야 합니다.')
                elif current_price <= 0:
                    st.error('현재 주가는 0보다 커야 합니다.')
                else:
                    # 계산 수행
                    total_investment = quantity * purchase_price
                    current_value = quantity * current_price
                    total_dividend = sum(monthly_dividends.values())
                    actual_profit_loss = current_value + total_dividend - total_investment
                    profit_rate = (actual_profit_loss / total_investment * 100) if total_investment > 0 else 0
                    
                    # 종목 정보 저장
                    stock_info = {
                        '종목명': stock_name,
                        '보유 수량': quantity,
                        '매수 단가': purchase_price,
                        '현재 주가': current_price,
                        '총 투자금': total_investment,
                        '현재 평가금': current_value,
                        '누적 배당금': total_dividend,
                        '실제 손익': actual_profit_loss,
                        '수익률 (%)': profit_rate,
                        '월별 배당금': monthly_dividends
                    }
                    
                    # 세션에 종목 추가
                    st.session_state.stocks.append(stock_info)
                    # 사용자 정보에 저장
                    user_manager.save_user_stocks(st.session_state.username, st.session_state.stocks)
                    st.success(f"{stock_name} 종목이 추가되었습니다.")
        
        # 종목 삭제 기능
        if st.session_state.stocks:
            st.subheader('종목 삭제')
            delete_options = [f"{i+1}. {stock['종목명']}" for i, stock in enumerate(st.session_state.stocks)]
            delete_index = st.selectbox('삭제할 종목 선택', options=delete_options, index=0)
            
            if st.button('선택 종목 삭제'):
                idx = int(delete_index.split('.')[0]) - 1
                removed_stock = st.session_state.stocks.pop(idx)
                # 사용자 정보에 저장
                user_manager.save_user_stocks(st.session_state.username, st.session_state.stocks)
                st.success(f"{removed_stock['종목명']} 종목이 삭제되었습니다.")
                st.rerun()
    
    # 상세 정보 탭
    with tab3:
        # 종목별 결과 테이블 표시
        if st.session_state.stocks:
            st.subheader('종목별 손익 현황')
            
            # 테이블용 데이터 준비
            table_data = []
            for stock in st.session_state.stocks:
                row = {
                    '종목명': stock['종목명'],
                    '보유 수량': stock['보유 수량'],
                    '매수 단가': f"{stock['매수 단가']:,.2f}",
                    '현재 주가': f"{stock['현재 주가']:,.2f}",
                    '총 투자금': f"{stock['총 투자금']:,.2f}",
                    '현재 평가금': f"{stock['현재 평가금']:,.2f}",
                    '누적 배당금': f"{stock['누적 배당금']:,.2f}",
                    '실제 손익': f"{stock['실제 손익']:,.2f}",
                    '수익률 (%)': f"{stock['수익률 (%)']:,.2f}%"
                }
                table_data.append(row)
            
            # 데이터프레임 생성 및 표시
            df = pd.DataFrame(table_data)
            st.table(df)
            
            # 전체 합계 계산
            total_investment = sum(stock['총 투자금'] for stock in st.session_state.stocks)
            total_current_value = sum(stock['현재 평가금'] for stock in st.session_state.stocks)
            total_dividend = sum(stock['누적 배당금'] for stock in st.session_state.stocks)
            total_profit_loss = sum(stock['실제 손익'] for stock in st.session_state.stocks)
            total_profit_rate = (total_profit_loss / total_investment * 100) if total_investment > 0 else 0
            
            # 합계 테이블 표시
            st.subheader('전체 합계')
            summary_data = {
                '항목': ['총 투자금', '총 평가금', '총 누적 배당금', '총 손익', '총 수익률'],
                '금액': [
                    f"{total_investment:,.2f}",
                    f"{total_current_value:,.2f}",
                    f"{total_dividend:,.2f}",
                    f"{total_profit_loss:,.2f}",
                    f"{total_profit_rate:,.2f}%"
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            st.table(summary_df)
            
            # 종목별 월간 배당금 상세 내역
            st.subheader('종목별 월간 배당금 상세')
            
            for i, stock in enumerate(st.session_state.stocks):
                st.markdown(f"**{i+1}. {stock['종목명']}**")
                
                # 배당금이 있는 월만 표시
                filtered_months = {month: amount for month, amount in stock['월별 배당금'].items() if amount > 0}
                
                if filtered_months:
                    monthly_data = {
                        '월': list(filtered_months.keys()),
                        '배당금': [f"{amount:,.2f}원" for amount in filtered_months.values()]
                    }
                    monthly_df = pd.DataFrame(monthly_data)
                    st.table(monthly_df)
                    
                    # 배당금 요약 정보
                    total_stock_dividend = sum(stock['월별 배당금'].values())
                    st.markdown(f"- 연간 총 배당금: **{total_stock_dividend:,.2f}원**")
                    st.markdown(f"- 배당 수익률: **{(total_stock_dividend / stock['총 투자금'] * 100):,.2f}%** (배당금 ÷ 투자금)")
                else:
                    st.info(f"{stock['종목명']}의 배당금 데이터가 없습니다.")
                
                st.markdown("---")
        else:
            st.info('종목을 추가하면 여기에 결과가 표시됩니다.') 
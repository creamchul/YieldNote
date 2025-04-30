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
# 환율 상태 초기화
if 'exchange_rate' not in st.session_state:
    st.session_state.exchange_rate = 1350.0  # 기본 환율 설정

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
    
    # 환율 설정
    col1, col2 = st.columns([3, 1])
    with col1:
        st.session_state.exchange_rate = st.number_input('달러-원 환율 설정', 
                                                        min_value=800.0, 
                                                        max_value=2000.0, 
                                                        value=st.session_state.exchange_rate, 
                                                        step=0.1, 
                                                        format="%.1f")
    with col2:
        st.info(f"1 USD = {st.session_state.exchange_rate:.1f} KRW")
    
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
            
            # 원화로 환산
            total_investment_krw = total_investment * st.session_state.exchange_rate
            total_current_value_krw = total_current_value * st.session_state.exchange_rate
            total_dividend_krw = total_dividend * st.session_state.exchange_rate
            total_profit_loss_krw = total_profit_loss * st.session_state.exchange_rate
            
            # 주요 지표 표시 (표 형태로)
            st.markdown("### 📈 주요 지표")
            
            summary_data = {
                '항목': ['총 투자금', '총 평가금', '총 배당금', '총 손익', '총 수익률'],
                'USD': [
                    f"${total_investment:,.2f}",
                    f"${total_current_value:,.2f}",
                    f"${total_dividend:,.2f}",
                    f"${total_profit_loss:,.2f}",
                    f"{total_profit_rate:,.2f}%"
                ],
                'KRW': [
                    f"₩{total_investment_krw:,.0f}",
                    f"₩{total_current_value_krw:,.0f}",
                    f"₩{total_dividend_krw:,.0f}",
                    f"₩{total_profit_loss_krw:,.0f}",
                    f"{total_profit_rate:,.2f}%"  # 수익률은 % 단위로 동일
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            st.table(summary_df)
            
            st.markdown("---")
            
            # 종목별 수익률 비교 (표 형태로)
            st.markdown("### 📊 종목별 수익률 비교")
            
            profit_data = []
            for stock in st.session_state.stocks:
                # 원화로 환산
                investment_krw = stock['총 투자금'] * st.session_state.exchange_rate
                value_krw = stock['현재 평가금'] * st.session_state.exchange_rate
                dividend_krw = stock['누적 배당금'] * st.session_state.exchange_rate
                profit_loss_krw = stock['실제 손익'] * st.session_state.exchange_rate
                
                profit_data.append({
                    '종목명': stock['종목명'],
                    '투자금 (USD)': f"${stock['총 투자금']:,.2f}",
                    '투자금 (KRW)': f"₩{investment_krw:,.0f}",
                    '평가금 (USD)': f"${stock['현재 평가금']:,.2f}",
                    '평가금 (KRW)': f"₩{value_krw:,.0f}",
                    '배당금 (USD)': f"${stock['누적 배당금']:,.2f}",
                    '배당금 (KRW)': f"₩{dividend_krw:,.0f}",
                    '수익/손실 (USD)': f"${stock['실제 손익']:,.2f}",
                    '수익/손실 (KRW)': f"₩{profit_loss_krw:,.0f}",
                    '수익률': f"{stock['수익률 (%)']:,.2f}%"
                })
            
            profit_df = pd.DataFrame(profit_data)
            # 수익률 기준으로 내림차순 정렬
            profit_df['수익률_정렬용'] = [stock['수익률 (%)'] for stock in st.session_state.stocks]
            profit_df = profit_df.sort_values('수익률_정렬용', ascending=False).drop('수익률_정렬용', axis=1)
            
            # USD/KRW 보기 선택 옵션
            currency_view = st.radio("통화 표시 방식", ["모두 표시", "USD만 표시", "KRW만 표시"], horizontal=True)
            
            if currency_view == "USD만 표시":
                columns_to_show = ['종목명', '투자금 (USD)', '평가금 (USD)', '배당금 (USD)', '수익/손실 (USD)', '수익률']
                profit_df_view = profit_df[columns_to_show]
            elif currency_view == "KRW만 표시":
                columns_to_show = ['종목명', '투자금 (KRW)', '평가금 (KRW)', '배당금 (KRW)', '수익/손실 (KRW)', '수익률']
                profit_df_view = profit_df[columns_to_show]
            else:
                profit_df_view = profit_df
            
            st.table(profit_df_view)
            
            st.markdown("---")
            
            # 포트폴리오 구성 비중 (표 형태로)
            st.markdown("### 🥧 포트폴리오 구성 비중")
            
            # 투자금 및 평가금 기준 비중 데이터 준비
            composition_data = []
            for stock in st.session_state.stocks:
                invest_pct = (stock['총 투자금'] / total_investment * 100) if total_investment > 0 else 0
                value_pct = (stock['현재 평가금'] / total_current_value * 100) if total_current_value > 0 else 0
                
                # 원화로 환산
                investment_krw = stock['총 투자금'] * st.session_state.exchange_rate
                value_krw = stock['현재 평가금'] * st.session_state.exchange_rate
                
                composition_data.append({
                    '종목명': stock['종목명'],
                    '투자금 (USD)': f"${stock['총 투자금']:,.2f}",
                    '투자금 (KRW)': f"₩{investment_krw:,.0f}",
                    '투자 비중': f"{invest_pct:.2f}%",
                    '평가금 (USD)': f"${stock['현재 평가금']:,.2f}",
                    '평가금 (KRW)': f"₩{value_krw:,.0f}",
                    '평가 비중': f"{value_pct:.2f}%"
                })
            
            composition_df = pd.DataFrame(composition_data)
            # 투자 비중 기준으로 내림차순 정렬
            composition_df['투자비중_정렬용'] = [(stock['총 투자금'] / total_investment * 100) if total_investment > 0 else 0 
                                        for stock in st.session_state.stocks]
            composition_df = composition_df.sort_values('투자비중_정렬용', ascending=False).drop('투자비중_정렬용', axis=1)
            
            # USD/KRW 보기 선택 옵션에 따라 표시
            if currency_view == "USD만 표시":
                columns_to_show = ['종목명', '투자금 (USD)', '투자 비중', '평가금 (USD)', '평가 비중']
                composition_df_view = composition_df[columns_to_show]
            elif currency_view == "KRW만 표시":
                columns_to_show = ['종목명', '투자금 (KRW)', '투자 비중', '평가금 (KRW)', '평가 비중']
                composition_df_view = composition_df[columns_to_show]
            else:
                composition_df_view = composition_df
                
            st.table(composition_df_view)
            
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
                '배당금 (USD)': [f"${amount:,.2f}" for amount in monthly_sums.values()],
                '배당금 (KRW)': [f"₩{amount * st.session_state.exchange_rate:,.0f}" for amount in monthly_sums.values()]
            }
            monthly_df = pd.DataFrame(monthly_data)
            
            # 배당금이 있는 월만 표시
            monthly_df['배당금_정렬용'] = list(monthly_sums.values())
            monthly_df_filtered = monthly_df[monthly_df['배당금_정렬용'] > 0].drop('배당금_정렬용', axis=1)
            
            if not monthly_df_filtered.empty:
                # USD/KRW 보기 선택 옵션에 따라 표시
                if currency_view == "USD만 표시":
                    columns_to_show = ['월', '배당금 (USD)']
                    monthly_df_view = monthly_df_filtered[columns_to_show]
                elif currency_view == "KRW만 표시":
                    columns_to_show = ['월', '배당금 (KRW)']
                    monthly_df_view = monthly_df_filtered[columns_to_show]
                else:
                    monthly_df_view = monthly_df_filtered
                    
                st.table(monthly_df_view)
                
                # 배당금 흐름 요약 텍스트
                max_month = monthly_df.loc[monthly_df['배당금_정렬용'].idxmax(), '월']
                max_amount = monthly_df['배당금_정렬용'].max()
                annual_dividend = sum(monthly_sums.values())
                
                st.markdown(f"**배당금 요약:**")
                st.markdown(f"- 연간 총 배당금: **${annual_dividend:,.2f}** (₩{annual_dividend * st.session_state.exchange_rate:,.0f})")
                st.markdown(f"- 배당금이 가장 많은 달: **{max_month}** (${max_amount:,.2f} / ₩{max_amount * st.session_state.exchange_rate:,.0f})")
                st.markdown(f"- 월 평균 배당금: **${(annual_dividend/12):,.2f}** (₩{(annual_dividend/12) * st.session_state.exchange_rate:,.0f})")
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
                quantity = st.number_input('보유 수량', min_value=0.0, value=0.0, step=0.01)
                purchase_price = st.number_input('매수 단가 (USD)', min_value=0.0, value=0.0, step=0.01)
            
            with col2:
                current_price = st.number_input('현재 주가 (USD)', min_value=0.0, value=0.0, step=0.01)
                st.write(f"매수 단가 (KRW): ₩{purchase_price * st.session_state.exchange_rate:,.0f}")
                st.write(f"현재 주가 (KRW): ₩{current_price * st.session_state.exchange_rate:,.0f}")
            
            st.subheader('월별 배당금 (USD)')
            
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
            
            # 종목 수정 기능
            st.subheader('종목 수정')
            edit_options = [f"{i+1}. {stock['종목명']}" for i, stock in enumerate(st.session_state.stocks)]
            
            # 종목 선택 및 수정 준비
            if 'editing_stock_idx' not in st.session_state:
                st.session_state.editing_stock_idx = None
            
            edit_index = st.selectbox('수정할 종목 선택', options=edit_options, index=0)
            select_idx = int(edit_index.split('.')[0]) - 1
            
            if st.button('종목 수정하기'):
                st.session_state.editing_stock_idx = select_idx
                st.rerun()
            
            # 선택한 종목 수정 폼 표시
            if st.session_state.editing_stock_idx is not None:
                idx = st.session_state.editing_stock_idx
                stock = st.session_state.stocks[idx]
                
                with st.form('edit_stock_form'):
                    st.subheader(f"'{stock['종목명']}' 종목 정보 수정")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        updated_name = st.text_input('종목명', value=stock['종목명'])
                        updated_quantity = st.number_input('보유 수량', min_value=0.0, value=stock['보유 수량'], step=0.01)
                        updated_purchase_price = st.number_input('매수 단가 (USD)', min_value=0.0, value=stock['매수 단가'], step=0.01)
                    
                    with col2:
                        updated_current_price = st.number_input('현재 주가 (USD)', min_value=0.0, value=stock['현재 주가'], step=0.01)
                        st.write(f"매수 단가 (KRW): ₩{updated_purchase_price * st.session_state.exchange_rate:,.0f}")
                        st.write(f"현재 주가 (KRW): ₩{updated_current_price * st.session_state.exchange_rate:,.0f}")
                    
                    st.subheader('월별 배당금 (USD)')
                    
                    # 한 줄에 4개 열로 배치
                    col1, col2, col3, col4 = st.columns(4)
                    
                    updated_monthly_dividends = {}
                    months = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
                    
                    for i, month in enumerate(months):
                        with [col1, col2, col3, col4][i % 4]:
                            default_value = stock['월별 배당금'].get(month, 0.0)
                            updated_monthly_dividends[month] = st.number_input(
                                month, 
                                min_value=0.0,
                                value=default_value,
                                step=0.01,
                                key=f"edit_dividend_{month}"
                            )
                    
                    update_button = st.form_submit_button('수정 완료')
                    cancel_button = st.form_submit_button('취소')
                    
                    if update_button:
                        if not updated_name:
                            st.error('종목명을 입력해주세요.')
                        elif updated_quantity <= 0:
                            st.error('보유 수량은 0보다 커야 합니다.')
                        elif updated_purchase_price <= 0:
                            st.error('매수 단가는 0보다 커야 합니다.')
                        elif updated_current_price <= 0:
                            st.error('현재 주가는 0보다 커야 합니다.')
                        else:
                            # 계산 수행
                            total_investment = updated_quantity * updated_purchase_price
                            current_value = updated_quantity * updated_current_price
                            total_dividend = sum(updated_monthly_dividends.values())
                            actual_profit_loss = current_value + total_dividend - total_investment
                            profit_rate = (actual_profit_loss / total_investment * 100) if total_investment > 0 else 0
                            
                            # 종목 정보 업데이트
                            updated_stock = {
                                '종목명': updated_name,
                                '보유 수량': updated_quantity,
                                '매수 단가': updated_purchase_price,
                                '현재 주가': updated_current_price,
                                '총 투자금': total_investment,
                                '현재 평가금': current_value,
                                '누적 배당금': total_dividend,
                                '실제 손익': actual_profit_loss,
                                '수익률 (%)': profit_rate,
                                '월별 배당금': updated_monthly_dividends
                            }
                            
                            # 세션에 종목 업데이트
                            st.session_state.stocks[idx] = updated_stock
                            # 사용자 정보에 저장
                            user_manager.save_user_stocks(st.session_state.username, st.session_state.stocks)
                            st.success(f"{updated_name} 종목 정보가 업데이트되었습니다.")
                            # 수정 모드 종료
                            st.session_state.editing_stock_idx = None
                            st.rerun()
                    
                    if cancel_button:
                        st.session_state.editing_stock_idx = None
                        st.rerun()
    
    # 상세 정보 탭
    with tab3:
        # 종목별 결과 테이블 표시
        if st.session_state.stocks:
            # USD/KRW 보기 선택 옵션
            currency_view_detail = st.radio("통화 표시 방식 (상세)", ["모두 표시", "USD만 표시", "KRW만 표시"], horizontal=True)
            
            st.subheader('종목별 손익 현황')
            
            # 테이블용 데이터 준비
            table_data = []
            for stock in st.session_state.stocks:
                # 원화로 환산
                purchase_price_krw = stock['매수 단가'] * st.session_state.exchange_rate
                current_price_krw = stock['현재 주가'] * st.session_state.exchange_rate
                total_investment_krw = stock['총 투자금'] * st.session_state.exchange_rate
                current_value_krw = stock['현재 평가금'] * st.session_state.exchange_rate
                total_dividend_krw = stock['누적 배당금'] * st.session_state.exchange_rate
                actual_profit_loss_krw = stock['실제 손익'] * st.session_state.exchange_rate
                
                if currency_view_detail == "USD만 표시":
                    row = {
                        '종목명': stock['종목명'],
                        '보유 수량': stock['보유 수량'],
                        '매수 단가': f"${stock['매수 단가']:,.2f}",
                        '현재 주가': f"${stock['현재 주가']:,.2f}",
                        '총 투자금': f"${stock['총 투자금']:,.2f}",
                        '현재 평가금': f"${stock['현재 평가금']:,.2f}",
                        '누적 배당금': f"${stock['누적 배당금']:,.2f}",
                        '실제 손익': f"${stock['실제 손익']:,.2f}",
                        '수익률 (%)': f"{stock['수익률 (%)']:,.2f}%"
                    }
                elif currency_view_detail == "KRW만 표시":
                    row = {
                        '종목명': stock['종목명'],
                        '보유 수량': stock['보유 수량'],
                        '매수 단가': f"₩{purchase_price_krw:,.0f}",
                        '현재 주가': f"₩{current_price_krw:,.0f}",
                        '총 투자금': f"₩{total_investment_krw:,.0f}",
                        '현재 평가금': f"₩{current_value_krw:,.0f}",
                        '누적 배당금': f"₩{total_dividend_krw:,.0f}",
                        '실제 손익': f"₩{actual_profit_loss_krw:,.0f}",
                        '수익률 (%)': f"{stock['수익률 (%)']:,.2f}%"
                    }
                else:
                    row = {
                        '종목명': stock['종목명'],
                        '보유 수량': stock['보유 수량'],
                        '매수 단가 (USD)': f"${stock['매수 단가']:,.2f}",
                        '매수 단가 (KRW)': f"₩{purchase_price_krw:,.0f}",
                        '현재 주가 (USD)': f"${stock['현재 주가']:,.2f}",
                        '현재 주가 (KRW)': f"₩{current_price_krw:,.0f}",
                        '총 투자금 (USD)': f"${stock['총 투자금']:,.2f}",
                        '총 투자금 (KRW)': f"₩{total_investment_krw:,.0f}",
                        '현재 평가금 (USD)': f"${stock['현재 평가금']:,.2f}",
                        '현재 평가금 (KRW)': f"₩{current_value_krw:,.0f}",
                        '누적 배당금 (USD)': f"${stock['누적 배당금']:,.2f}",
                        '누적 배당금 (KRW)': f"₩{total_dividend_krw:,.0f}",
                        '실제 손익 (USD)': f"${stock['실제 손익']:,.2f}",
                        '실제 손익 (KRW)': f"₩{actual_profit_loss_krw:,.0f}",
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
            
            # 원화로 환산
            total_investment_krw = total_investment * st.session_state.exchange_rate
            total_current_value_krw = total_current_value * st.session_state.exchange_rate
            total_dividend_krw = total_dividend * st.session_state.exchange_rate
            total_profit_loss_krw = total_profit_loss * st.session_state.exchange_rate
            
            # 합계 테이블 표시
            st.subheader('전체 합계')
            
            if currency_view_detail == "USD만 표시":
                summary_data = {
                    '항목': ['총 투자금', '총 평가금', '총 누적 배당금', '총 손익', '총 수익률'],
                    '금액': [
                        f"${total_investment:,.2f}",
                        f"${total_current_value:,.2f}",
                        f"${total_dividend:,.2f}",
                        f"${total_profit_loss:,.2f}",
                        f"{total_profit_rate:,.2f}%"
                    ]
                }
            elif currency_view_detail == "KRW만 표시":
                summary_data = {
                    '항목': ['총 투자금', '총 평가금', '총 누적 배당금', '총 손익', '총 수익률'],
                    '금액': [
                        f"₩{total_investment_krw:,.0f}",
                        f"₩{total_current_value_krw:,.0f}",
                        f"₩{total_dividend_krw:,.0f}",
                        f"₩{total_profit_loss_krw:,.0f}",
                        f"{total_profit_rate:,.2f}%"
                    ]
                }
            else:
                summary_data = {
                    '항목': ['총 투자금', '총 평가금', '총 누적 배당금', '총 손익', '총 수익률'],
                    'USD': [
                        f"${total_investment:,.2f}",
                        f"${total_current_value:,.2f}",
                        f"${total_dividend:,.2f}",
                        f"${total_profit_loss:,.2f}",
                        f"{total_profit_rate:,.2f}%"
                    ],
                    'KRW': [
                        f"₩{total_investment_krw:,.0f}",
                        f"₩{total_current_value_krw:,.0f}",
                        f"₩{total_dividend_krw:,.0f}",
                        f"₩{total_profit_loss_krw:,.0f}",
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
                    if currency_view_detail == "USD만 표시":
                        monthly_data = {
                            '월': list(filtered_months.keys()),
                            '배당금 (USD)': [f"${amount:,.2f}" for amount in filtered_months.values()]
                        }
                    elif currency_view_detail == "KRW만 표시":
                        monthly_data = {
                            '월': list(filtered_months.keys()),
                            '배당금 (KRW)': [f"₩{amount * st.session_state.exchange_rate:,.0f}" for amount in filtered_months.values()]
                        }
                    else:
                        monthly_data = {
                            '월': list(filtered_months.keys()),
                            '배당금 (USD)': [f"${amount:,.2f}" for amount in filtered_months.values()],
                            '배당금 (KRW)': [f"₩{amount * st.session_state.exchange_rate:,.0f}" for amount in filtered_months.values()]
                        }
                    
                    monthly_df = pd.DataFrame(monthly_data)
                    st.table(monthly_df)
                    
                    # 배당금 요약 정보
                    total_stock_dividend = sum(stock['월별 배당금'].values())
                    total_stock_dividend_krw = total_stock_dividend * st.session_state.exchange_rate
                    dividend_yield = (total_stock_dividend / stock['총 투자금'] * 100) if stock['총 투자금'] > 0 else 0
                    
                    if currency_view_detail == "USD만 표시":
                        st.markdown(f"- 연간 총 배당금: **${total_stock_dividend:,.2f}**")
                    elif currency_view_detail == "KRW만 표시":
                        st.markdown(f"- 연간 총 배당금: **₩{total_stock_dividend_krw:,.0f}**")
                    else:
                        st.markdown(f"- 연간 총 배당금: **${total_stock_dividend:,.2f}** (₩{total_stock_dividend_krw:,.0f})")
                    
                    st.markdown(f"- 배당 수익률: **{dividend_yield:,.2f}%** (배당금 ÷ 투자금)")
                else:
                    st.info(f"{stock['종목명']}의 배당금 데이터가 없습니다.")
                
                st.markdown("---")
        else:
            st.info('종목을 추가하면 여기에 결과가 표시됩니다.') 
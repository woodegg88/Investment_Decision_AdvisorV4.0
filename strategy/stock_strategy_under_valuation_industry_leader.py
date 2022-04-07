#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Tang Zhuangkun

'''
# TODO
股票监控策略，处于绝对低估位置的行业龙头
满足条件：
1、沪深300成分股
2、公认的行业龙头，https://xueqiu.com/8132581807/216258901
3、有记录的交易日数据超过1500天--2500天，即至少超过6.17年--10年的上市时间，仅看10年以内的指标（每年约243个交易日）
4、涨幅超过x%，就抛出进行轮动，坚守纪律性；这个指标需要回测来判断；
5、实时PB, 实时PE, 实时扣非PE（当时涨跌幅*昨日扣非PE）处于处于历史最低水平，即 拉通历史来看，处于倒数5位以内
'''


'''
-- 统计每年平均有多少个交易日
select avg(totoal_trading_days) from
(
select trading_year,count(*) as totoal_trading_days from
(select substr(trading_date,1,4) as trading_year
from trading_days
where trading_date<'2022-01-01'
) as raw
group by trading_year) raw_two

2005	242
2006	241
2007	242
2008	246
2009	244
2010	242
2011	244
2012	243
2013	238
2014	245
2015	244
2016	244
2017	244
2018	243
2019	244
2020	243
2021	243

'''



'''
-- 获取股票，股票名称，最新日期，市净率，市净率低估排名，共有该股票多少交易日记录，当前市净率位于历史百分比位置
select raw.stock_code, raw.stock_name, raw.date, raw.pb, raw.rank_num, record.total_record, raw.percent_num from 
(select stock_code, stock_name, date, pb,
rank() OVER (partition by stock_code ORDER BY pb asc) AS rank_num,  
percent_rank() OVER (partition by stock_code ORDER BY pb asc) AS percent_num
from stocks_main_estimation_indexes_historical_data) raw
left join 
(select stock_code, count(1) as total_record from stocks_main_estimation_indexes_historical_data group by stock_code) as record
on raw.stock_code = record.stock_code
where raw.date = (select max(date) from stocks_main_estimation_indexes_historical_data)
and record.total_record>1500
order by raw.percent_num asc;

-- 效果如 
600201	生物股份	2022-04-07	2.4402423138242970	1	2944	0
603866	桃李面包	2022-04-07	3.8300289940574705	3	1528	0.0013097576948264572
600000	浦发银行	2022-04-07	0.4308040872445288	18	2929	0.005806010928961749
601818	光大银行	2022-04-07	0.4847183905791494	18	2805	0.006062767475035664
600016	民生银行	2022-04-07	0.3489460092537104	23	2967	0.007417397167902899
601155	新城控股	2022-04-07	1.2309878673186585	18	1529	0.01112565445026178
600015	华夏银行	2022-04-07	0.3771476418174968	64	2957	0.02131258457374831
300146	汤臣倍健	2022-04-07	3.4025785285744368	57	2574	0.021764477263894286
601398	工商银行	2022-04-07	0.5916731966013162	66	2963	0.021944632005401754
000002	万科A	2022-04-07	1.0302332587489198	74	2821	0.025886524822695035
601939	建设银行	2022-04-07	0.6279756638616979	78	2964	0.025987175160310495
600597	光明乳业	2022-04-07	1.9467722644235010	86	2891	0.029411764705882353
000869	张裕Ａ	2022-04-07	1.8226508997219684	89	2961	0.02972972972972973
601288	农业银行	2022-04-07	0.5263202443663337	87	2844	0.030249736194161096
000961	中南建设	2022-04-07	0.5815674850847055	90	2937	0.030313351498637602
000671	阳光城	2022-04-07	0.5470418664477901	97	2902	0.033092037228541885
002146	荣盛发展	2022-04-07	0.4078522781617524	101	2934	0.03409478349812479
600648	外高桥	2022-04-07	1.3471860708200998	102	2928	0.03450632046463956
000656	金科股份	2022-04-07	0.7365313814048178	102	2893	0.03492392807745505

'''






'''
-- 获取股票，股票名称，最新日期，扣非市盈率率，扣非市盈率率低估排名，共有该股票多少交易日记录，当前扣非市盈率率位于历史百分比位置
select raw.stock_code, raw.stock_name, raw.date, raw.pe_ttm_nonrecurring, raw.rank_num, record.total_record, raw.percent_num from
(select stock_code, stock_name, date, pe_ttm_nonrecurring,
rank() OVER (partition by stock_code ORDER BY pe_ttm_nonrecurring asc) AS rank_num,
percent_rank() OVER (partition by stock_code ORDER BY pe_ttm_nonrecurring asc) AS percent_num
from stocks_main_estimation_indexes_historical_data) raw
left join
(select stock_code, count(*) as total_record from stocks_main_estimation_indexes_historical_data group by stock_code) as record
on raw.stock_code = record.stock_code
where raw.date = (select max(date) from stocks_main_estimation_indexes_historical_data)
and record.total_record>1500
order by raw.percent_num asc;

-- 效果如 
603866	桃李面包	2022-04-07	26.4062387322165720	3	1528	0.0013097576948264572
002511	中顺洁柔	2022-04-07	21.5256754399666370	52	2716	0.01878453038674033
600895	张江高科	2022-04-07	12.0794516852419630	60	2968	0.01988540613414223
601818	光大银行	2022-04-07	4.2020367359736280	60	2805	0.021041369472182596
600015	华夏银行	2022-04-07	3.7188474206319655	77	2957	0.02571041948579161
000876	新希望	2022-04-07	-14.8742832973529890	74	2788	0.026193039110154286
000998	隆平高科	2022-04-07	-120.8900611587226900	93	2808	0.032775204845030284
600873	梅花生物	2022-04-07	13.2214675653753400	93	2781	0.033093525179856115
000537	广宇发展	2022-04-07	-44.8147889443359800	98	2829	0.0342998585572843
000540	中天金融	2022-04-07	-10.2908161401282640	93	2555	0.036021926389976505
300498	温氏股份	2022-04-07	-11.3514109608347430	58	1553	0.03672680412371134
000031	大悦城	2022-04-07	-149.9908804589785200	120	2782	0.042790363178712695
601998	中信银行	2022-04-07	4.4429322212606510	139	2958	0.046668921203922895
601288	农业银行	2022-04-07	4.4845803185909480	137	2844	0.04783679212099894
601169	北京银行	2022-04-07	4.2517218511923530	150	2924	0.05097502565856996
000961	中南建设	2022-04-07	3.4266848226092360	154	2937	0.052111716621253405
601988	中国银行	2022-04-07	4.4738749439161550	156	2962	0.05234718000675447
601328	交通银行	2022-04-07	4.3793931290461080	192	2962	0.06450523471800068
002481	双塔食品	2022-04-07	35.0915181178522700	174	2665	0.06493993993993993
'''


import 'package:final_project/model/member_model.dart';
import 'package:final_project/screen/login_page.dart';
import 'package:final_project/screen/mypage/mypage.dart';
import 'package:final_project/screen/smart_home/smart_home.dart';
import 'package:final_project/screen/week/week_sentiment_analysis.dart';
import 'package:flutter/material.dart';
import 'package:final_project/screen/today/today_sentiment_analysis.dart';

class Bottom extends StatefulWidget {
  const Bottom({Key? key, required this.member}) : super(key: key);
  final MemberModel member;

  @override
  State<Bottom> createState() => _BottomState();
}

class _BottomState extends State<Bottom> {
  int _selectedIndex = 1; // 처음에 "오늘의감정" 페이지 선택
  String appBarTitle = '오늘의감정';
  String? appBarIconPath;

  late List<Widget> _widgetList = [
    Week(),
    Today(),
    SmartHome(),
    Mypage(member: widget.member), // 멤버 페이지 넘김
  ];

  late final MemberModel member;

  @override
  void initState() {
    super.initState();
    // 앱 실행 시 처음에 "오늘의감정" 페이지 선택
    _selectedIndex = 1;
    _updateAppBar(1); // 초기 앱바 설정
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (appBarIconPath != null) Image.asset(appBarIconPath!, width: 30, height: 30), //앱바 아이콘 크기
            if (appBarIconPath != null) SizedBox(width: 8),
            Text(appBarTitle),
          ],
        ),
        centerTitle: true, // title을 가운데 정렬
        backgroundColor: Colors.amber, // 앱바 배경색
        foregroundColor: Colors.black,
        elevation: 0.0,
        bottom: PreferredSize(
          preferredSize: Size.fromHeight(11), // AppBar의 높이를 설정
          child: SizedBox(),
        ),
      ),
      body: _widgetList[_selectedIndex], // 선택된 페이지를 표시
      bottomNavigationBar: BottomNavigationBar(
        items: [
          BottomNavigationBarItem(
            icon: ImageIcon(AssetImage('image/graph.png')),
            label: '감정분석',
          ),
          BottomNavigationBarItem(
            icon: ImageIcon(AssetImage('image/today_emotion.png')),
            label: '오늘의감정',
          ),
          BottomNavigationBarItem(
            icon: ImageIcon(AssetImage('image/home_control.png')),
            label: '스마트홈',
          ),
          BottomNavigationBarItem(
              icon: ImageIcon(AssetImage('image/mypage.png')),
              label: '마이페이지'
          ),
        ],
        showUnselectedLabels: true,
        selectedItemColor: Colors.black,
        unselectedItemColor: Colors.black,
        backgroundColor: Colors.white,
        onTap: _onItemTapped, // 항목을 탭했을 때 호출되는 콜백 함수
        currentIndex: _selectedIndex, // 현재 선택된 인덱스
      ),
    );
  }

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index; // 선택된 인덱스 업데이트
      _updateAppBar(index); // 앱바 업데이트
    });
  }

  void _updateAppBar(int index) {
    switch (index) {
      case 0:
        appBarTitle = '감정분석';
        appBarIconPath = 'image/graph.png'; // 감정분석 아이콘 설정
        break;
      case 1:
        appBarTitle = '오늘의감정';
        appBarIconPath = 'image/today_emotion.png'; // 오늘의감정 아이콘 설정
        break;
      case 2:
        appBarTitle = '스마트홈';
        appBarIconPath = 'image/home_control.png'; // 스마트홈 아이콘 설정
        break;
      case 3:
        appBarTitle = '마이페이지';
        appBarIconPath = 'image/mypage.png'; // 마이페이지 아이콘 설정
        break;
      default:
        appBarTitle = '';
        appBarIconPath = null; // 기본값으로 아이콘을 null로 설정
    }
  }
}

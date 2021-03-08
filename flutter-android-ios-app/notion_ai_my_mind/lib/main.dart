import 'dart:async';
import 'dart:ui';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:notion_ai_my_mind/Arguments.dart';
import 'package:notion_ai_my_mind/list_view.dart';

import 'package:notion_ai_my_mind/overlay_view.dart';
import 'package:notion_ai_my_mind/resources/strings.dart';
import 'package:notion_ai_my_mind/settings.dart';
import 'package:receive_sharing_intent/receive_sharing_intent.dart';
import 'package:rxdart/rxdart.dart';

import 'package:webview_flutter/webview_flutter.dart';
import 'package:notion_ai_my_mind/api/api.dart';


import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:rxdart/subjects.dart';
import 'package:timezone/data/latest.dart' as tz;
import 'package:timezone/timezone.dart' as tz;

final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
FlutterLocalNotificationsPlugin();

/// Streams are created so that app can respond to notification-related events
/// since the plugin is initialised in the `main` function
final BehaviorSubject<ReceivedNotification> didReceiveLocalNotificationSubject =
BehaviorSubject<ReceivedNotification>();

final BehaviorSubject<String> selectNotificationSubject =
BehaviorSubject<String>();

const MethodChannel platform =
MethodChannel('dexterx.dev/flutter_local_notifications_example');

class ReceivedNotification {
  ReceivedNotification({
    @required this.id,
    @required this.title,
    @required this.body,
    @required this.payload,
  });

  final int id;
  final String title;
  final String body;
  final String payload;
}

final GlobalKey<NavigatorState> navigatorKey = new GlobalKey<NavigatorState>();
String selectedNotificationPayload;
bool isSharing = false;

Future<void> main() async {
  // needed if you intend to initialize in the `main` function
  WidgetsFlutterBinding.ensureInitialized();

  //await _configureLocalTimeZone();

  final NotificationAppLaunchDetails notificationAppLaunchDetails =
  await flutterLocalNotificationsPlugin.getNotificationAppLaunchDetails();

  const AndroidInitializationSettings initializationSettingsAndroid =
  AndroidInitializationSettings('@mipmap/ic_launcher');

  /// Note: permissions aren't requested here just to demonstrate that can be
  /// done later
  final IOSInitializationSettings initializationSettingsIOS =
  IOSInitializationSettings(
      requestAlertPermission: false,
      requestBadgePermission: false,
      requestSoundPermission: false,
      onDidReceiveLocalNotification:
          (int id, String title, String body, String payload) async {
        didReceiveLocalNotificationSubject.add(ReceivedNotification(
            id: id, title: title, body: body, payload: payload));
      });
  const MacOSInitializationSettings initializationSettingsMacOS =
  MacOSInitializationSettings(
      requestAlertPermission: false,
      requestBadgePermission: false,
      requestSoundPermission: false);
  final InitializationSettings initializationSettings = InitializationSettings(
      android: initializationSettingsAndroid,
      iOS: initializationSettingsIOS,
      macOS: initializationSettingsMacOS);
  await flutterLocalNotificationsPlugin.initialize(initializationSettings,
      onSelectNotification: (String payload) async {
        if (payload != null) {
          debugPrint('notification payload: $payload');
        }
        selectedNotificationPayload = payload;
        selectNotificationSubject.add(payload);
      });

  String initialRoute = MyHomePage.routeName;
  /*if(isSharing){
    initialRoute = AddLinkPage.routeName;
  }*/

  runApp(
    MaterialApp(
      navigatorKey: navigatorKey,
      theme: ThemeData(primarySwatch: Colors.teal, accentColor: Color(0xFFDD5237)),
      home: MyHomePage(notificationAppLaunchDetails),
      routes: {
        '/add': (BuildContext context) => AddLinkPage(),
        '/collection':  (BuildContext context) => CollectionListPage(),
      },
    ),
  );
}

Future<void> _configureLocalTimeZone() async {
  tz.initializeTimeZones();
  final String timeZoneName = await platform.invokeMethod('getTimeZoneName');
  tz.setLocalLocation(tz.getLocation(timeZoneName));
}

class MyHomePage extends StatefulWidget {

    const MyHomePage(
    this.notificationAppLaunchDetails, {
      Key key,
    }) : super(key: key);

    static const String routeName = '/';

    final NotificationAppLaunchDetails notificationAppLaunchDetails;

    bool get didNotificationLaunchApp =>
        notificationAppLaunchDetails?.didNotificationLaunchApp ?? false;

    @override
    _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyHomePage> with WidgetsBindingObserver {
  final Completer<WebViewController> _controller =
  Completer<WebViewController>();
  StreamSubscription _intentDataStreamSubscription;
  List<SharedMediaFile> _sharedFiles;
  String _sharedText;


  @override
  void initState() {
    super.initState();
    _requestPermissions();
    _configureDidReceiveLocalNotificationSubject();
    _configureSelectNotificationSubject();
    _initShareIntent();
    WidgetsBinding.instance.addObserver(this);
  }

  void _initShareIntent() {
    // For sharing images coming from outside the app while the app is in the memory
    _intentDataStreamSubscription = ReceiveSharingIntent.getMediaStream()
        .listen((List<SharedMediaFile> value) {

      setState(() {
        _sharedFiles = value;
        isSharing = true;
      });

      if(_sharedFiles != null) {
        String uri = (_sharedFiles?.map((f) => f.path)?.join(",") ?? "");
        if (uri != null) {
          navigatorKey.currentState.pushNamed(CollectionListPage.routeName, arguments: Arguments(uri,true,0,navigatorKey));
        }
      }

      setState(() {
        _sharedFiles = null;
        isSharing = true;
      });

    }, onError: (err) {
      print("getIntentDataStream error: $err");
    });

    // For sharing images coming from outside the app while the app is closed
    ReceiveSharingIntent.getInitialMedia().then((List<SharedMediaFile> value) {
      setState(() {
        _sharedFiles = value;
        isSharing = false;
      });

      if(_sharedFiles != null) {
        String uri = (_sharedFiles?.map((f) => f.path)?.join(",") ?? "");

        if (uri != null) {
          navigatorKey.currentState.pushNamed(CollectionListPage.routeName, arguments: Arguments(uri,true,0,navigatorKey));
        }
      }

      setState(() {
        _sharedFiles = null;
        isSharing = false;
      });

    });

    // For sharing or opening urls/text coming from outside the app while the app is in the memory
    _intentDataStreamSubscription =
        ReceiveSharingIntent.getTextStream().listen((String value) {
          setState(() {
            _sharedText = value;
            isSharing = true;
          });

          if(_sharedText != null) {
            print("Main activity: " + _sharedText);

            Fluttertoast.showToast(msg: "shared: $_sharedText",
                toastLength: Toast.LENGTH_SHORT,
                gravity: ToastGravity.BOTTOM);

            navigatorKey.currentState.pushNamed(CollectionListPage.routeName, arguments: Arguments(_sharedText,false,0,navigatorKey));

          }else{
            print("Main activity: is null");
          }

          setState(() {
            _sharedText = null;
          });

        }, onError: (err) {
          Fluttertoast.showToast(msg: "getLinkStream error: $err",
              toastLength: Toast.LENGTH_SHORT,
              gravity: ToastGravity.BOTTOM);
          print("getLinkStream error: $err");
        });


    // For sharing or opening urls/text coming from outside the app while the app is closed
    ReceiveSharingIntent.getInitialText().then((String value) {
      setState(() {
        _sharedText = value;
        isSharing = true;
      });

      if (_sharedText != null) {
        print("Main activity app closed: " + _sharedText);

        Fluttertoast.showToast(msg: "Shared when closed: $_sharedText",
            toastLength: Toast.LENGTH_SHORT,
            gravity: ToastGravity.BOTTOM);

        navigatorKey.currentState.pushNamed(CollectionListPage.routeName, arguments: Arguments(_sharedText,false,0,navigatorKey));
      }else{
        print("Main activity app closed: is null");
      }

        setState(() {
          _sharedText = null;
        });
    });
  }

  void _requestPermissions() {
    flutterLocalNotificationsPlugin
        .resolvePlatformSpecificImplementation<
        IOSFlutterLocalNotificationsPlugin>()
        ?.requestPermissions(
      alert: true,
      badge: true,
      sound: true,
    );
    flutterLocalNotificationsPlugin
        .resolvePlatformSpecificImplementation<
        MacOSFlutterLocalNotificationsPlugin>()
        ?.requestPermissions(
      alert: true,
      badge: true,
      sound: true,
    );
  }

  void _configureDidReceiveLocalNotificationSubject() {
    didReceiveLocalNotificationSubject.stream
        .listen((ReceivedNotification receivedNotification) async {
      await showDialog(
        context: context,
        builder: (BuildContext context) => CupertinoAlertDialog(
          title: receivedNotification.title != null
              ? Text(receivedNotification.title)
              : null,
          content: receivedNotification.body != null
              ? Text(receivedNotification.body)
              : null,
        ),
      );
    });
  }

  void _configureSelectNotificationSubject() {
    selectNotificationSubject.stream.listen((String payload) async {
      //await Navigator.pushNamed(context, '/secondPage');
    });
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if(state == AppLifecycleState.resumed){
      print("App resumed");

      Fluttertoast.showToast(msg: "App resumed",
          toastLength: Toast.LENGTH_SHORT,
          gravity: ToastGravity.BOTTOM);
    }else if(state == AppLifecycleState.inactive){
      print("App Inactive");
      setState(() {
        isSharing = false;
      });
      Fluttertoast.showToast(msg: "App Inactive",
          toastLength: Toast.LENGTH_SHORT,
          gravity: ToastGravity.BOTTOM);
    }else if(state == AppLifecycleState.paused){
      print("App paused");
      Fluttertoast.showToast(msg: "App paused",
          toastLength: Toast.LENGTH_SHORT,
          gravity: ToastGravity.BOTTOM);
    }else if(state == AppLifecycleState.detached){
      print("App detached");
      Fluttertoast.showToast(msg: "App detached",
          toastLength: Toast.LENGTH_SHORT,
          gravity: ToastGravity.BOTTOM);
    }
  }

  @override
  void dispose() {
    didReceiveLocalNotificationSubject.close();
    selectNotificationSubject.close();
    WidgetsBinding.instance.removeObserver(this);
    _intentDataStreamSubscription.cancel();
    super.dispose();
  }

  Future<void> _onMindLoaded() async {
    const AndroidNotificationDetails androidPlatformChannelSpecifics =
    AndroidNotificationDetails(
        'your channel id', 'your channel name', 'your channel description',
        importance: Importance.max,
        priority: Priority.high,
        ticker: 'ticker');
    const NotificationDetails platformChannelSpecifics = NotificationDetails(
      android: androidPlatformChannelSpecifics,
    );
    await flutterLocalNotificationsPlugin.show(
        0, null, 'Your mind loaded succesfully!', platformChannelSpecifics,
        payload: 'item x');
  }

  Future<void> _onContentAdded() async {
    const AndroidNotificationDetails androidPlatformChannelSpecifics =
    AndroidNotificationDetails(
        'your channel id', 'your channel name', 'your channel description',
        importance: Importance.max,
        priority: Priority.high,
        ticker: 'ticker');
    const NotificationDetails platformChannelSpecifics = NotificationDetails(
      android: androidPlatformChannelSpecifics,
    );
    await flutterLocalNotificationsPlugin.show(
        0, null, 'Added to your mind.', platformChannelSpecifics,
        payload: 'item x');
  }

  Future<void> _onContentError() async {
    const AndroidNotificationDetails androidPlatformChannelSpecifics =
    AndroidNotificationDetails(
        'your channel id', 'your channel name', 'your channel description',
        importance: Importance.max,
        priority: Priority.high,
        ticker: 'ticker');
    const NotificationDetails platformChannelSpecifics = NotificationDetails(
      android: androidPlatformChannelSpecifics,
    );
    await flutterLocalNotificationsPlugin.show(
        0, null, 'Content could not be added to your mind.', platformChannelSpecifics,
        payload: 'item x');

    await flutterLocalNotificationsPlugin.show(
        0, null, 'Make sure the ip/port are corrects, and the server is running. Or that you are not sharing invalid content.', platformChannelSpecifics,
        payload: 'item x');
  }

  Future<String> _calculation = Api().getMindUrl();

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData(primarySwatch: Colors.teal, accentColor: Color(0xFFDD5237)),
      home: Scaffold(
        appBar: AppBar(
          title:  const Text(Strings.title),
        ),
        body: FutureBuilder<String>(
          future: _calculation, // a previously-obtained Future<String> or null
          builder: (BuildContext context, AsyncSnapshot<String> snapshot) {
            List<Widget> children;
            if (snapshot.hasData) {
              return _buildButtons(context,snapshot.data);
            } else if (snapshot.hasError) {
              children = <Widget>[
                Icon(
                  Icons.error_outline,
                  color: Colors.red,
                  size: 60,
                ),
                Padding(
                  padding: const EdgeInsets.only(top: 16),
                  child: Text('Error: ${snapshot.error}'),
                )
              ];
            } else {
              children = <Widget>[
                SizedBox(
                  child: CircularProgressIndicator(),
                  width: 60,
                  height: 60,
                ),
                const Padding(
                  padding: EdgeInsets.only(top: 16),
                  child: Text(Strings.waitText),
                )
              ];
            }
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: children,
              ),
            );
          },
        ),
        floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
        floatingActionButton: _buildFab(
            context),
      ),
    );
  }

  Widget _buildFab(BuildContext context) {
    return new Container(
      padding: EdgeInsets.only(bottom: 5.0),
      child: Align(
        alignment: Alignment.bottomCenter,
        child: FloatingActionButton(
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => settings()),
            );
          },
          tooltip: 'Settings',
          child: Icon(Icons.settings),
          focusColor: Colors.red,
          elevation: 3.0,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.all(Radius.circular(16.0))),
        ),

      ),
    );
  }

  Widget _buildButtons(BuildContext context,String url) {
    return new Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            SizedBox(height: 25),
            new Text('Welcome to your mind!',textAlign: TextAlign.center,
              overflow: TextOverflow.visible,
              style: TextStyle(fontWeight: FontWeight.bold,fontSize: 30)),
            SizedBox(height: 50),
            ButtonTheme(
              minWidth: 200.0,
              height: 100.0,
              child: RaisedButton(
                onPressed:() => Api().launchURL(url),
                splashColor: Color(0xFFDD5237),
                color: Colors.teal,
                child: new Text(
                  "Open Your Mind",
                  style: new TextStyle(fontSize: 20.0, color: Colors.white),
                ),
              ),
            ),
            SizedBox(height: 30),
            ButtonTheme(
              minWidth: 200.0,
              height: 100.0,
              child: RaisedButton(
                onPressed:() => Api().launchSettings(),
                splashColor: Color(0xFFDD5237),
                color: Colors.teal,
                child: new Text(
                  "Open Server Settings",
                  style: new TextStyle(fontSize: 20.0, color: Colors.white),
                ),
              ),
            ),
            SizedBox(height: 30),
            ButtonTheme(
              minWidth: 200.0,
              height: 50.0,
              child: RaisedButton(
                onPressed:() => Api().refreshCollections().then((value) => _buildRefreshNot()),
                splashColor: Color(0xFFDD5237),
                color: Colors.teal,
                child: new Text(
                  "Refresh collections",
                  style: new TextStyle(fontSize: 20.0, color: Colors.white),
                ),
              ),
            ),
            SizedBox(height: 30),
            new Text('Made with love by @elblogbruno! Have any problem or feedback? Post an issue!', textAlign: TextAlign.center,
                overflow: TextOverflow.visible,
                style: TextStyle(fontWeight: FontWeight.bold,fontSize: 20)),
            SizedBox(height: 10),
            new RaisedButton(
              onPressed:() => Api().launchRepo(),
              splashColor: Color(0xFFDD5237),
              color: Colors.teal,
              child: new Text(
                "Open Github Repo",
                style: new TextStyle(fontSize: 20.0, color: Colors.white),
              ),
            ),

          ],
        )
      ),
    );
  }
  Widget _buildRefreshNot(){
    return AlertDialog(
      // Retrieve the text the that user has entered by using the
      // TextEditingController.
      title: Text("Collections refreshed"),
      content: Text("Succesfully refreshed the collections"),
    );
  }

  Widget _buildWebView(BuildContext context,String url){
      return new WebView(
        initialUrl: url,
        javascriptMode: JavascriptMode.unrestricted,
        onWebViewCreated: (WebViewController webViewController) {
          _controller.complete(webViewController);
        },
        // TODO(iskakaushik): Remove this when collection literals makes it to stable.
        // ignore: prefer_collection_literals
        javascriptChannels: <JavascriptChannel>[
          _toasterJavascriptChannel(context),
        ].toSet(),
        navigationDelegate: (NavigationRequest request) {
          if (request.url.startsWith('https://www.youtube.com/')) {
            print('blocking navigation to $request}');
            return NavigationDecision.prevent;
          }
          print('allowing navigation to $request');
          return NavigationDecision.navigate;
        },
        onPageStarted: (String url) {
          print('Page started loading: $url');
        },
        onPageFinished: (String url) {
          print('Page finished loading: $url');
          _onMindLoaded();
        },
        gestureNavigationEnabled: true,
      );
    }

  JavascriptChannel _toasterJavascriptChannel(BuildContext context) {
    return JavascriptChannel(
        name: 'Toaster',
        onMessageReceived: (JavascriptMessage message) {
          Scaffold.of(context).showSnackBar(
            SnackBar(content: Text(message.message)),
          );
        });
  }

}

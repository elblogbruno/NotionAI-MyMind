import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:http/io_client.dart';
import 'package:notion_ai_my_mind/settings.dart';
import 'dart:async';

import 'package:receive_sharing_intent/receive_sharing_intent.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:notion_ai_my_mind/api/api.dart';


void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return new MaterialApp(
      title: 'Flutter Demo',
      theme: new ThemeData(
        // This is the theme of your application.
        //
        // Try running your application with "flutter run". You'll see the
        // application has a blue toolbar. Then, without quitting the app, try
        // changing the primarySwatch below to Colors.green and then invoke
        // "hot reload" (press "r" in the console where you ran "flutter run",
        // or press Run > Flutter Hot Reload in IntelliJ). Notice that the
        // counter didn't reset back to zero; the application is not restarted.
        primarySwatch: Colors.blue,
        //primaryColor: Colors.red,
        //backgroundColor: Colors.white,
        //bottomAppBarColor: Colors.white,
      ),
      home: new MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyHomePage> {
  final Completer<WebViewController> _controller =
  Completer<WebViewController>();
  StreamSubscription _intentDataStreamSubscription;
  List<SharedMediaFile> _sharedFiles;
  String _sharedText;
  String imageUrl;

  @override
  void initState() {
    super.initState();

    Fluttertoast.showToast(msg: "app loaded",
                  toastLength: Toast.LENGTH_SHORT,
                  gravity: ToastGravity.BOTTOM);
    // For sharing images coming from outside the app while the app is in the memory
    _intentDataStreamSubscription = ReceiveSharingIntent.getMediaStream()
        .listen((List<SharedMediaFile> value) {
      setState(() {
        _sharedFiles = value;
        Fluttertoast.showToast(msg: "Shared:" + (_sharedFiles?.map((f) => f.path)?.join(",") ?? ""),
                  toastLength: Toast.LENGTH_SHORT,
                  gravity: ToastGravity.BOTTOM);

        print("Shared:" + (_sharedFiles?.map((f) => f.path)?.join(",") ?? ""));
      });
    }, onError: (err) {
      print("getIntentDataStream error: $err");
    });
  
    // For sharing images coming from outside the app while the app is closed
    ReceiveSharingIntent.getInitialMedia().then((List<SharedMediaFile> value) {
      setState(() {
        _sharedFiles = value;
        Fluttertoast.showToast(msg: "Shared:" + (_sharedFiles?.map((f) => f.path)?.join(",") ?? ""),
                          toastLength: Toast.LENGTH_SHORT,
                          gravity: ToastGravity.BOTTOM);

        print("Shared:" + (_sharedFiles?.map((f) => f.path)?.join(",") ?? ""));
      });
    });

    // For sharing or opening urls/text coming from outside the app while the app is in the memory
    _intentDataStreamSubscription =
        ReceiveSharingIntent.getTextStream().listen((String value) {
          setState(() {
            _sharedText = value;
            if(_sharedText != " ") {
              Api().addUrlToMind(_sharedText, "Url from: $_sharedText");
              print("Shared: $_sharedText");

              Fluttertoast.showToast(msg: "Shared: $_sharedText",
                  toastLength: Toast.LENGTH_SHORT,
                  gravity: ToastGravity.BOTTOM);
            }
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

        if(_sharedText != " ") {
          Api().addUrlToMind(_sharedText, "Url from: $_sharedText");
          print("Shared: $_sharedText");

          Fluttertoast.showToast(msg: "Shared: $_sharedText",
              toastLength: Toast.LENGTH_SHORT,
              gravity: ToastGravity.BOTTOM);
        }

      });
    });
  }

  @override
  void dispose() {
    _intentDataStreamSubscription.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    const textStyleBold = const TextStyle(fontWeight: FontWeight.bold);
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(
          title: const Text('Notion AI My Mind'),
        ),
        body: FutureBuilder(
          // render content via the builder
          builder: (context, snapshot) {
            // render content if data is available

            if (snapshot.hasData) {
              var data = snapshot.data;
              print(data);
              return _BuildWebView(context,data);
            }
            // show a spinner until the data is available
            return new CircularProgressIndicator();
          },
          // source of data for the builder
          future: Api().getMindUrl(Api().getServerUrl().toString() + "get_current_mind_url"),
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
            tooltip: 'Increment',
            child: Icon(Icons.settings),
            focusColor: Colors.red,
            elevation: 3.0,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.all(Radius.circular(16.0))),
          ),
        ),
      );
    }

    Widget _BuildWebView(BuildContext context,String url){
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
          return showDialog(
            context: context,
            builder: (context) {
              return AlertDialog(
                // Retrieve the text the that user has entered by using the
                // TextEditingController.
                content: Text("Your Mind Loaded!"),
              );

            },
          );
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

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:notion_ai_my_mind/Arguments.dart';
import 'package:notion_ai_my_mind/main.dart';
import 'package:notion_ai_my_mind/resources/strings.dart';
import 'package:fluttertoast/fluttertoast.dart';

import 'api/api.dart';

class AddLinkPage extends StatelessWidget  {
  static const String routeName = '/add';

  @override
  Widget build(BuildContext context) {
    final Arguments args = ModalRoute.of(context).settings.arguments;
    return Scaffold(
        appBar: AppBar(
          title: const Text(Strings.titleAddNewLinkPage),
        ),
        body: FutureBuilder<String>(
          future:  Api().addContentToMind(args.url,args.isImage), // a previously-obtained Future<String> or null
          builder: (BuildContext context, AsyncSnapshot<String> snapshot) {
            List<Widget> children;
            if (snapshot.hasData) {
              return _buildText(context,snapshot.data.toString(), snapshot.data == '-1');
            } else if (snapshot.hasError) {
              return _buildText(context,snapshot.error.toString(), true);
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
    );
  }

  Widget _buildText(BuildContext context,String text,bool error) {
    List<Widget> children;
    if(text == '200'){
        text = Strings.goodResultResponse;
    }
    if(error){
      children = <Widget>[
        Icon(
          Icons.error_outline,
          color: Colors.red,
          size: 200,
        ),
        Padding(
          padding: const EdgeInsets.only(top: 16),
          child: Text(text,textAlign: TextAlign.center ,style: new TextStyle(fontSize: 20.0, color: Colors.black)),
        ),
        SizedBox(height: 50),
        RaisedButton(
          onPressed:()=> Navigator.of(context).pop(),
          splashColor: Color(0xFFDD5237),
          color: Colors.teal,
          child: new Text(
            Strings.exitButtonText,
            style: new TextStyle(fontSize: 20.0, color: Colors.white),
          ),
        )
      ];
    }else{
      children = <Widget>[
        Icon(
          Icons.check_circle_outline,
          color: Colors.green,
          size: 200,
        ),
        Padding(
          padding: const EdgeInsets.only(top: 16),
          child: Text(text,textAlign: TextAlign.center ,style: new TextStyle(fontSize: 20.0, color: Colors.black)),
        ),
        SizedBox(height: 50),
        RaisedButton(
          onPressed:()=> Navigator.of(context).pop(),
          splashColor: Color(0xFFDD5237),
          color: Colors.teal,
          child: new Text(
            Strings.exitButtonText,
            style: new TextStyle(fontSize: 20.0, color: Colors.white),
          ),
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
  }
}



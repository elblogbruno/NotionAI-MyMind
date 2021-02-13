import 'dart:io';

import 'package:flutter/material.dart';
import 'package:notion_ai_my_mind/resources/strings.dart';

import 'api/api.dart';

class AddLinkPage extends StatefulWidget {
  static const String routeName = '/add';
  final String url;
  final bool isImage;
  AddLinkPage({Key key, this.url,this.isImage}) : super(key: key);

  @override
  State<StatefulWidget> createState() => _ShowUrlState();
}

class _ShowUrlState extends State<AddLinkPage> {

  Future<String> status;

  //Future<String> _calculation = Api().addContentToMind(widget.url,widget.isImage);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
          title: const Text(Strings.titleAddNewLinkPage),
        ),
        body: FutureBuilder<String>(
          future:  Api().addContentToMind(widget.url,widget.isImage), // a previously-obtained Future<String> or null
          builder: (BuildContext context, AsyncSnapshot<String> snapshot) {
            List<Widget> children;
            if (snapshot.hasData) {
              return _buildText(context,snapshot.data,true);
            } else if (snapshot.hasError) {
              return _buildText(context,snapshot.error.toString(),false);
            } else {
              children = <Widget>[
                SizedBox(
                  child: CircularProgressIndicator(),
                  width: 60,
                  height: 60,
                ),
                const Padding(
                  padding: EdgeInsets.only(top: 16),
                  child: Text('Awaiting result...'),
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
    if(error){
      children = <Widget>[
        Icon(
          Icons.error_outline,
          color: Colors.red,
          size: 200,
        ),
        Padding(
          padding: const EdgeInsets.only(top: 16),
          child: Text(text,textScaleFactor: 3,),
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
          child: Text(text,textScaleFactor: 3,),
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



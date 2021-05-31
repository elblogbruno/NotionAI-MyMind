import 'package:flutter/material.dart';
import 'package:flutter_link_preview/flutter_link_preview.dart';
import 'package:flutter_tagging/flutter_tagging.dart';
import 'package:notion_ai_my_mind/Arguments.dart';
import 'package:notion_ai_my_mind/api/models/multi_select_tag_list_response.dart';


import 'package:notion_ai_my_mind/resources/strings.dart';
import 'api/TagSearchService.dart';
import 'api/api.dart';
import 'dart:math';

import 'api/models/api_response.dart';
import 'api/models/tag.dart';
import 'locales/main.i18n.dart';

Random random = new Random();

class AddLinkPage extends StatelessWidget  {
  static const String routeName = '/add';

  String _selectedValuesJson = 'Nothing to show';
  List<Tag> _Tags;
  APIResponse block_response;

  Arguments args;
  @override
  Widget build(BuildContext context) {
    args = ModalRoute.of(context).settings.arguments;
    return Scaffold(
      resizeToAvoidBottomInset: false, //https://stackoverflow.com/questions/63743330/how-to-a-renderflex-overflowed-by-61-pixels-on-the-bottom-on-the-top-of-the-v
      appBar: AppBar(
        title:  Text(Strings.titleAddNewLinkPage.i18n),
      ),
      body: FutureBuilder<APIResponse>(
        future:  Api().addContentToMind(args.url,args.isImage,args.collection_index), // a previously-obtained Future<String> or null
        builder: (BuildContext context, AsyncSnapshot<APIResponse> snapshot) {
          List<Widget> children;
          if (snapshot.hasData) {
            return _buildText(context,snapshot.data);
          } else if (snapshot.hasError) {
            return _buildText(context,snapshot.error);
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

  final titleController = TextEditingController();
  final urlController = TextEditingController();

  /*Builds final response based on request*/
  Widget _buildText(BuildContext context,APIResponse response) {
    List<Widget> children;
    block_response = response;
    if(response.status_text == "error"){
      children = <Widget>[
        Icon(
          Icons.error_outline,
          color: Colors.red,
          size: 200,
        ),
        Padding(
          padding: const EdgeInsets.only(top: 10),
          child: Text(response.text_response,textAlign: TextAlign.center ,style: new TextStyle(fontSize: 20.0, color: Colors.black)),
        ),
        SizedBox(height: 50),
        ElevatedButton(
          onPressed:()=> Navigator.of(context).pop(),
          style: ElevatedButton.styleFrom(
            primary: Colors.teal,
          ),
          child: Icon(
            Icons.close,
            color: Colors.white,
            size: 50,
          ),
        ),
      ];
    }else{
      children = <Widget>[
        SizedBox(height: 20),
        Icon(
          Icons.check,
          color: Colors.green,
          size: 150,
        ),
        SizedBox(height: 10),
        Text(response.text_response,textAlign: TextAlign.center ,style: new TextStyle(fontSize: 20.0, color: Colors.black)),
        SizedBox(height: 30),
        _TagRequest(),
        SizedBox(height: 50),

        Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            ElevatedButton(
              onPressed:()=> buildModifyDialog(context,response),
              style: ElevatedButton.styleFrom(
                primary: Colors.teal,
              ),
              child:  Icon(
                Icons.edit,
                color: Colors.white,
                size: 50,
              ),
            ),
            ElevatedButton(
              onPressed: () => Api().launchURL(response.block_url),
              style: ElevatedButton.styleFrom(
                primary: Colors.teal,
              ),
              child:Icon(
                Icons.open_in_browser,
                color: Colors.white,
                size: 50,
              ),
            ),
            ElevatedButton(
              onPressed: () => Navigator.of(context).pop(),
              style: ElevatedButton.styleFrom(
                primary: Colors.teal,
              ),
              child:  Icon(
                Icons.exit_to_app,
                color: Colors.white,
                size: 50,
              ),
            ),
          ],
        ),
        SizedBox(height: 30),

      ];
    }

    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: children,
      ),
    );
  }

  /*Makes the tag request to get available tags*/
  Widget _TagRequest(){
    return FutureBuilder<MultiSelectTagListResponse>(
      future:  Api().get_multi_select_tags(args.collection_index), // a previously-obtained Future<String> or null
      builder: (BuildContext context, AsyncSnapshot<MultiSelectTagListResponse> snapshot) {
        List<Widget> children;
        if (snapshot.hasData) {
          return _buildDropDown(context, snapshot.data);
        } else if (snapshot.hasError) {
          return _buildDropDown(context, snapshot.data);
        } else {
          children = <Widget>[
            SizedBox(
              child: CircularProgressIndicator(),
              width: 60,
              height: 60,
            ),
            Padding(
              padding: EdgeInsets.only(top: 16),
              child: Text(Strings.waitText.i18n),
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
      });
  }

  /*Builds the dropwdown with the tags*/
  Widget _buildDropDown(context, MultiSelectTagListResponse response){

    if(response == null || response.multi_select_tag_list.isEmpty){
      return Card(
        child:  Column(
            children: <Widget> [
                Text(response.response.text_response)
              ],
        ),
      );
    }else{
      _Tags = [];
      TagSearchService.tagList = response.multi_select_tag_list;
      return Card(
        child:  Column(
            children: <Widget> [
              FlutterTagging<Tag>(
                initialItems: _Tags,
                textFieldConfiguration: TextFieldConfiguration(
                  decoration: InputDecoration(
                    border: InputBorder.none,
                    filled: true,
                    fillColor: Colors.green.withAlpha(30),
                    hintText: 'Search Tags',
                    labelText: Strings.addTagsText.i18n,
                  ),
                ),
                findSuggestions: TagSearchService.getTags,
                additionCallback: (value) {
                  return Tag(option_name: value,option_id: value,option_color: value);
                },
                onAdded: (language){
                  // api calls here, triggered when add to tag button is pressed
                  print(language.option_name);
                  return Tag();
                },
                configureSuggestion: (lang)
                {
                  return SuggestionConfiguration(
                    title:Text(lang.option_name),
                    additionWidget: Chip(
                      avatar: Icon(
                        Icons.add_circle,
                        color: Colors.white,
                      ),
                      label: Text('Add New Tag'),
                      labelStyle: TextStyle(
                        color: Colors.white,
                        fontSize: 14.0,
                        fontWeight: FontWeight.w300,
                      ),
                      backgroundColor: Colors.green,
                    ),
                  );
                },
                configureChip: (lang) {
                  return ChipConfiguration(
                    label: Text(lang.option_name),
                    backgroundColor: colorFor(lang.option_color),
                    labelStyle: TextStyle(color: Colors.white),
                    deleteIconColor: Colors.white,
                  );
                },
                onChanged: () {
                  _selectedValuesJson = _Tags
                      .map<String>((lang) => '\n${lang.toJson()}')
                      .toList()
                      .toString();
                  _selectedValuesJson =
                      _selectedValuesJson.replaceFirst('}]', '}\n]');
                },
              ),
              ElevatedButton(
                onPressed:()=> showDialog(context: context, builder: (x) => _AddTagsToBlockRequest(context)),
                style: ElevatedButton.styleFrom(
                  primary: Colors.teal,
                ),
                child: new Text(
                  Strings.addTagsText.i18n,
                  style: new TextStyle(fontSize: 20.0, color: Colors.white),
                ),
              ),
            ]

        ),
      );
    }

  }

  /*Makes the request to add tags*/
  Widget _AddTagsToBlockRequest(BuildContext context) {
    return FutureBuilder<APIResponse>(
        future:  Api().set_multi_select_tags(args.collection_index,block_response.block_url, _Tags), // a previously-obtained Future<String> or null
        builder: (BuildContext context, AsyncSnapshot<APIResponse> snapshot) {
          List<Widget> children;
          if (snapshot.hasData) {
            if (snapshot.data.status_code != 200){
              Future.delayed(Duration(seconds: 4), () {
                Navigator.of(context, rootNavigator: true).pop('dialog');
                _Tags.clear();
              });
              final dialog = AlertDialog(
                  content: Center(
                    child: Column(
                      children: <Widget>[
                        Text(snapshot.data.text_response),
                        Icon(
                          Icons.error_outline,
                          color: Colors.red,
                          size: 50,
                        ),

                      ],
                    ),
                  )
              );
              return dialog;
            }else{
              final dialog = AlertDialog(
                content: Icon(
                  Icons.check,
                  color: Colors.green,
                  size: 50,
                ),
              );

              return dialog;
            }


          } else if (snapshot.hasError) {
            String error = "Error adding tags.";
            final dialog = AlertDialog(
              content: Center(
                child: Column(
                  children: <Widget>[
                    Text(error),
                    Icon(
                      Icons.error_outline,
                      color: Colors.red,
                      size: 50,
                    ),

                  ],
                ),
              )
            );
            Future.delayed(Duration(seconds: 4), () {
              Navigator.of(context, rootNavigator: true).pop('dialog');
            });
            return dialog;
          } else {
            children = <Widget>[
              SizedBox(
                child: CircularProgressIndicator(),
                width: 60,
                height: 60,
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
        });
  }

  /*Gets the color from a hexstring*/
  Color colorFor(String hexString){
    final buffer = StringBuffer();
    if (hexString.length == 6 || hexString.length == 7) buffer.write('ff');
    buffer.write(hexString.replaceFirst('#', ''));
    return Color(int.parse(buffer.toString(), radix: 16));
  }


  /*Builds a dialog to modify title and url on block*/
  Future<dynamic> buildModifyDialog(context,APIResponse response){
    return showDialog(
      context: context,
      builder: (context)
    {
      String url = block_response.block_attached_url;
      String title = block_response.block_title;
      return StatefulBuilder(
          builder: (context, setState) {
            return Dialog(
              // Retrieve the text the that user has entered by using the
              // TextEditingController.
                backgroundColor: Colors.transparent,
                insetPadding: EdgeInsets.all(10),
                child: Stack(
                  alignment: Alignment.center,
                  children: <Widget>[
                    Container(
                        width: double.infinity,
                        height: 450,
                        decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(10),
                            color: Colors.white
                        ),
                        padding: EdgeInsets.fromLTRB(10, 5, 10, 10),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.spaceAround,
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: <Widget>[
                            Text(Strings.currentTitleTitle.i18n,
                                style: TextStyle(fontSize: 24),
                                textAlign: TextAlign.center
                            ),
                            Container(
                                child: Row(
                                  children: <Widget>[
                                    Flexible(
                                        child: new Text(title))
                                  ],
                                )),
                            TextField(
                              decoration: InputDecoration(
                                border: OutlineInputBorder(),
                                labelText: title,
                                hintText: "Modify Title",
                              ),
                              controller: titleController,
                            ),
                            Text(Strings.currentUrlTitle.i18n,
                                style: TextStyle(fontSize: 24),
                                textAlign: TextAlign.center
                            ),
                            Container(
                                child: Row(
                                  children: <Widget>[
                                    Flexible(
                                        child: Padding(
                                          padding: EdgeInsets.only(top: 5 , bottom: 5, left: 5, right: 5),
                                          child: FlutterLinkPreview(
                                            url: url,
                                            titleStyle: TextStyle(
                                              color: Colors.blue,
                                              fontWeight: FontWeight.bold,
                                            ),
                                          ),
                                        )
                                    )
                                  ],
                                )),
                            TextField(
                              decoration: InputDecoration(
                                border: OutlineInputBorder(),
                                labelText: url,
                                hintText: "Modify URL",
                              ),
                              controller: urlController,
                            ),
                            ElevatedButton(
                              onPressed: () => showDialog(context: context, builder: (x) => _modifyBlock(context,response)),
                              style: ElevatedButton.styleFrom(
                                primary: Colors.teal,
                              ),
                              child: new Text(
                                Strings.modifyTitleText.i18n,
                                style: new TextStyle(fontSize: 20.0, color: Colors.white),
                              ),
                            ),
                          ],
                        )
                    ),
                    Positioned(
                      top: -100,
                      child: Container(
                        width: 250,
                        height: 50,
                        decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(10),
                            color: Colors.white
                        ),
                        padding: EdgeInsets.fromLTRB(5, 10, 5, 5),
                        child: Text(Strings.modifyTitleText.i18n,
                            style: TextStyle(fontSize: 24),
                            textAlign: TextAlign.center
                        ),
                      ),
                    )
                  ],
                )
            );
          });
    });

  }

  /*Makes the request to modify the block and returns a dialog.*/
  Widget _modifyBlock(BuildContext context, APIResponse response) {
    return FutureBuilder<APIResponse>(
        future:  Api().modify_element_by_id(
        response.block_url, titleController.text,
        urlController.text, response), // a previously-obtained Future<String> or null
        builder: (BuildContext context, AsyncSnapshot<APIResponse> snapshot) {
          List<Widget> children;
          if (snapshot.hasData) {
            block_response = snapshot.data;
            /*url = block_response.block_attached_url;
            title = block_response.block_title;*/
            final dialog = _buildModifiedNot(context,snapshot.data);
            return dialog;
          } else if (snapshot.hasError) {
            final dialog = _buildModifiedNot(context,snapshot.error);
            return dialog;
          } else {
            children = <Widget>[
              SizedBox(
                child: CircularProgressIndicator(),
                width: 60,
                height: 60,
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
        });
  }

  /*Creates the response dialog.*/
  Widget _buildModifiedNot(context,APIResponse response) {
    List<Widget> children;
    children = <Widget>[
      Text(response.text_response),
      SizedBox(height: 50),
    ];
    if (response.status_text == "error"){
      children.add(
          ElevatedButton(
            onPressed: () => Navigator.of(context, rootNavigator: true).pop('dialog'),
            style: ElevatedButton.styleFrom(
              primary: Colors.teal,
            ),

            child:  Icon(
              Icons.close,
              color: Colors.white,
              size: 50,
            ),
          ),
      );
    }
    else{
      children.add(
        ElevatedButton(
          onPressed: () => Navigator.of(context, rootNavigator: true).pop('dialog'),
          style: ElevatedButton.styleFrom(
            primary: Colors.teal,
          ),

          child:  Icon(
            Icons.check,
            color: Colors.white,
            size: 50,
          ),
        ),
      );
    }
    return AlertDialog(
        // Retrieve the text the that user has entered by using the
        // TextEditingController.
        title: Text(response.block_title),
        content: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: children
            ),
    );
  }

  /*Clears the text written*/
  void clearText() {
    Future.delayed(Duration.zero, () {
      titleController.clear();
      urlController.clear();
    });
  }
}


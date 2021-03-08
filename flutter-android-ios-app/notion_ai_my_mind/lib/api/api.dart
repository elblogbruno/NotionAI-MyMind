import 'dart:convert';


import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:http/http.dart' as http;
import 'package:notion_ai_my_mind/api/APICollectionResponse.dart';
import 'package:notion_ai_my_mind/api/apicollection.dart';
import 'package:notion_ai_my_mind/api/apiresponse.dart';
import 'package:notion_ai_my_mind/resources/strings.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:path/path.dart';
import 'package:async/async.dart';
import 'dart:io';

import 'package:url_launcher/url_launcher.dart';

class Api {
  Future<String> refreshCollections() async {
    try {
      String _serverUrl = await getServerUrl();

      String serverUrl = _serverUrl + "get_mind_structure";
      print("get_mind_structure: " + serverUrl);
      http.Response response = await http.get(serverUrl);

      if (response.statusCode == 200) {
        setCollections(response.body.toString());
        return '200';
      } else {
        return '-1';
      }
    } catch (_) {
      return '-1';
    }
  }
  Future<String> getMindUrl() async {
    try {
      String _serverUrl = await getServerUrl();

      String serverUrl = _serverUrl + "get_current_mind_url";
      print("GetMindUrl: " + serverUrl);
      http.Response response = await http.get(serverUrl);

      if (response.statusCode == 200) {
        return response.body.toString();
      } else {
        return '-1';
      }
    } catch (_) {
      return '-1';
    }
  }

  Future<APIResponse> addUrlToMind(String urlToAdd,int collection_index) async {
    try {
      RegExp exp = new RegExp(r'(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+');
      Iterable<RegExpMatch> matches = exp.allMatches(urlToAdd);
      print(matches.length);
      if (matches == null) {

      } else {
          if(matches.length == 0) //means no url extracted on the text. it is just text.
          {
            String title = "unknown url added to your mind from Phone";
            String _serverUrl = await getServerUrl();
            String finalUrl = _serverUrl + "add_text_to_mind?collection_index="+collection_index.toString() + "&url=" + title + "&text=" + urlToAdd;
            print("Final sharing url: " + finalUrl);
            http.Response response = await http.get(finalUrl);

            if (response.statusCode == 200) {
              return parseResponse(response.body);
            } else {
              return createBadResponse();
            }
          }
          else if(urlToAdd == matches.first.group(0)) {
            print(matches.first.group(0));

            final matchedText = matches.first.group(0);
            print("Match: " + matchedText); // my

            String title = matchedText + " added to your mind from Phone";
            String _serverUrl = await getServerUrl();
            String finalUrl = _serverUrl + "add_url_to_mind?collection_index="+collection_index.toString() + "&url=" + matchedText + "&title=" + title;
            print("Final sharing url: " + finalUrl);
            http.Response response = await http.get(finalUrl);


            if (response.statusCode == 200) {
              return  parseResponse(response.body);
            } else {
              return createBadResponse();
            }
          }else{
            print(matches.first.group(0));

            final matchedText = matches.first.group(0);
            print("Match: " + matchedText); // my

            String _serverUrl = await getServerUrl();
            String finalUrl = _serverUrl + "add_text_to_mind?collection_index="+collection_index.toString() + "&url=" + matchedText + "&text=" + urlToAdd;

            print("Final sharing url: " + finalUrl);
            http.Response response = await http.get(finalUrl);

            if (response.statusCode == 200) {
              return  parseResponse(response.body);
            } else {
              return createBadResponse();
            }
          }

      }

    } catch (e) {

      Fluttertoast.showToast(msg: "Error: $e",
          toastLength: Toast.LENGTH_SHORT,
          gravity: ToastGravity.BOTTOM);

      return createBadResponse();
    }
  }

  Future<String> addImageToMind(String urlToAdd) async {
    try {

      String title = urlToAdd + " added to your mind from Phone";
      String _serverUrl = await getServerUrl();
      String finalUrl = _serverUrl + "add_image_to_mind?url="+urlToAdd+"&image_src="+title+"&image_src_url="+title;

      print("Final sharing url: " + finalUrl);

      http.Response response = await http.get(finalUrl);

      if (response.statusCode == 200) {
        return "200";
      } else {
        return '-1';
      }
    } catch (_) {
      return '-1';
    }
  }

  Future<String> setCollectionIndex(int index) async {
    try {

      String _serverUrl = await getServerUrl();
      String finalUrl = _serverUrl + "set_collection_index?collection_index="+index.toString();

      print("Final setCollectionIndex url: " + finalUrl);

      http.Response response = await http.get(finalUrl);

      if (response.statusCode == 200) {
        return "200";
      } else {
        return '-1';
      }
    } catch (_) {
      return '-1';
    }
  }


  Future<APIResponse> uploadImage(File imageFile,int index) async {
    setCollectionIndex(index);

    var stream = new http.ByteStream(DelegatingStream.typed(imageFile.openRead()));
    var length = await imageFile.length();

    String _serverUrl = await getServerUrl();
    String uploadURL = _serverUrl + "upload_file";
    print("Final upload url: " + uploadURL);

    var uri = Uri.parse(uploadURL);
    var request = new http.MultipartRequest("POST", uri);
    var multipartFile = new http.MultipartFile('file', stream, length,
        filename: basename(imageFile.path));
    //contentType: new MediaType('image', 'png'));

    request.files.add(multipartFile);
    var response = await request.send();
    print(response.statusCode);

    var response1 = await http.Response.fromStream(response);

    if (response.statusCode == 200) {
      return parseResponse(response1.body);
    } else {
      return createBadResponse();
    }
  }

  Future<APIResponse> addContentToMind(String url,bool isImage,int index) async{
    print("addContentToMind: " + url + " " + isImage.toString());
    if(url != null){
      print("Widget url: " + url);
      if(isImage){
        print("Widget is image");
        var myFile = new File(url);
        return uploadImage(myFile,index);
      }else{
        print("Widget is url");
        return addUrlToMind(url,index);
      }
    }else{
      return createBadResponse();
    }
  }

  APIResponse parseResponse(String responseBody) {
    Map userMap = jsonDecode(responseBody);
    var response = APIResponse.fromJson(userMap);
    return response;
  }

  APIResponse createBadResponse() {
    return APIResponse(
      status_code: -1,
      text_response: Strings.badResultResponse,
      status_text: Strings.badResultResponse,
      block_url: Strings.badResultResponse,
    );
  }

  setCollections(String value) async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();

    await prefs.setString("structure", value);
  }


  Future<List<APICollection>> getCollections() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    String structure = prefs.getString("structure") ?? 'name';

    return parseStructure(structure);
  }

  List<APICollection> parseStructure(String responseBody) {
    Map map = jsonDecode(responseBody);
    List<dynamic> data = map["structure"];

    List<APICollection> collectionList = new List<APICollection>();

    for(int i = 0; i < data.length;i++){
      //Map userMap = jsonDecode(data[i]);
      Map<String, dynamic> myMap = new Map<String, dynamic>.from(data[i]);
      print(myMap);
      var response = APICollection.fromJson(myMap);
      collectionList.add(response);
    }

    return collectionList;
  }

  setServerUrl(String value) async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();

    if (value[value.length-1] != "/"){
      value = value + "/";
    }

    await prefs.setString("url", value);
  }


  Future<String> getServerUrl() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    return prefs.getString("url") ?? 'name';
  }




  launchSettings() async {
    String _serverUrl = await getServerUrl();
    launchURL(_serverUrl);
  }
  launchRepo() async {
    launchURL("https://github.com/elblogbruno/NotionAI-MyMind");
  }

  launchURL(String url) async {
    if (await canLaunch(url)) {
      await launch(url);
    } else {
      throw 'Could not launch $url';
    }
  }
}
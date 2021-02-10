import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:path/path.dart';
import 'package:async/async.dart';
import 'dart:io';

class Api {

  Future<String> getMindUrl() async {
    try {
      String _serverUrl = await getServerUrl();

      String serverUrl = _serverUrl + "get_current_mind_url";
      print("GetMindUrl: " + serverUrl);
      http.Response response = await http.get(serverUrl);

      if (response.statusCode == 200) {
        return "200";
      } else {
        return '-1';
      }
    } catch (_) {
      return '-1';
    }
  }

  Future<String> addUrlToMind(String urlToAdd) async {
    try {
      RegExp exp = new RegExp(r'(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+');
      Iterable<RegExpMatch> matches = exp.allMatches(urlToAdd);

      matches.forEach((match) {
        print(urlToAdd.substring(match.start, match.end));
      });

      if (matches == null) {
        print("No match");
      } else {
        final matchedText = matches.elementAt(1).group(0);
        print(matchedText); // my

        String title = urlToAdd + " added to your mind from Phone";
        String _serverUrl = await getServerUrl();
        String finalUrl = _serverUrl + "add_url_to_mind?url="+urlToAdd+"&title="+title;
        print("Final sharing url: " + finalUrl);
        http.Response response = await http.get(finalUrl);

        if (response.statusCode == 200) {
          return "200";
        } else {
          return '-1';
        }
      }

    } catch (_) {
      return '-1';
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

  setServerUrl(String value) async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setString("url", value);
  }


  Future<String> getServerUrl() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    return prefs.getString("url") ?? 'name';
  }



  Future<String> uploadImage(File imageFile) async {
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

    if (response.statusCode == 200) {
      return '200';
    } else {
      return '-1';
    }
  }
}
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class Api {

  Future<String> getMindUrl(String serverUrl) async {
    try {
      print(serverUrl);
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

  Future<String> addUrlToMind(String urlToAdd,String title) async {
    try {
      print(urlToAdd);
      http.Response response = await http.get(getServerUrl().toString() + "add_url_to_mind?url="+urlToAdd+"&title="+title);

      if (response.statusCode == 200) {
        return response.body.toString();
      } else {
        return '-1';
      }
    } catch (_) {
      return '-1';
    }
  }

  Future<bool> setServerUrl(String value) async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    return prefs.setString("url", value);
  }


  Future<String> getServerUrl() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    return prefs.getString("url") ?? 'name';
  }
}
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';

String uploadUrl = "http://192.168.1.100:5000/api";
String downloadUrl = "http://192.168.1.100:5000/result";

Future? getData() async {
  try {
    http.Response response = await http.get(Uri.tryParse(uploadUrl)!).timeout(
      const Duration(seconds: 5),
      onTimeout: () {
        throw Exception("Timeout");
      },
    );
    return jsonDecode(response.body);
  } catch (e) {
    return null;
  }
}

Future<bool> uploadImage(XFile imageFile) async {
  String base64Image = base64Encode(File(imageFile.path).readAsBytesSync());
  try {
    http.Response response =
        await http.post(Uri.tryParse(uploadUrl)!, body: base64Image);
    print(response);
    return true;
  } catch (e) {
    print(e);
  }
  return false;
}

import Foundation
import Vision
import AppKit
for file in CommandLine.arguments.dropFirst() {
 do {
  let url = URL(fileURLWithPath:file)
  let req = VNRecognizeTextRequest()
  req.recognitionLevel = .accurate
  req.recognitionLanguages = ["zh-Hans", "en-US"]
  req.usesLanguageCorrection = false
  try VNImageRequestHandler(url:url, options:[:]).perform([req])
  let lines = (req.results ?? []).compactMap { obs -> [String:Any]? in
    guard let s = obs.topCandidates(1).first else {return nil}
    return ["text":s.string, "confidence":s.confidence, "x":obs.boundingBox.minX,"y":obs.boundingBox.minY]
  }
  let data = try JSONSerialization.data(withJSONObject:lines, options:[.prettyPrinted,.sortedKeys])
  try data.write(to: url.deletingPathExtension().appendingPathExtension("ocr.json"))
 }catch{fputs("OCR failed: \(file)\n",stderr)}
}

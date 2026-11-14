import Foundation
import Vision
import AppKit
let input = CommandLine.arguments[1]
let url = URL(fileURLWithPath: input)
let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = true
let handler = VNImageRequestHandler(url: url)
do {
  try handler.perform([request])
  let lines = (request.results ?? []).compactMap { $0.topCandidates(1).first?.string }
  let output = try JSONSerialization.data(withJSONObject: ["text": lines.joined(separator: "\n")])
  FileHandle.standardOutput.write(output)
} catch {
  FileHandle.standardError.write(Data("OCR failed: \(error)\n".utf8))
  exit(1)
}

/*
helper function grab decks
*/

function openalldecks() {
  var lineReader = require("readline").createInterface({
    input: require("fs").createReadStream("file.in")
  });

  lineReader.on("line", function(line) {
    console.log("Line from file:", line);
  });
}

module.exports = {
  openalldecks: openalldecks
};

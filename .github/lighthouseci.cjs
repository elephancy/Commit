// Local checked-in/built pages only; never upload to public report storage.
module.exports = {
  "ci": {
    "collect": {
      "staticDistDir": "./.",
      "url": [
        "http://localhost/"
      ],
      "numberOfRuns": 1,
      "isSinglePageApplication": false
    },
    "assert": {
      "assertions": {
        "categories:accessibility": [
          "error",
          {
            "minScore": 0.9
          }
        ],
        "categories:performance": [
          "warn",
          {
            "minScore": 0.8
          }
        ],
        "categories:seo": [
          "warn",
          {
            "minScore": 0.9
          }
        ]
      }
    },
    "upload": {
      "target": "filesystem",
      "outputDir": "./artifacts/lighthouse"
    }
  }
};

(ns tweetlocker.core
  (:require [fs.core :as fs]
            [cheshire.core :as json]))

(def ^:dynamic *data-root* (System/getenv "DATA_ROOT"))
(def ^:dynamic *kinds* #{:tweet :reply :retweet :favorite :dm})

(defn get-user-path
  "Get a path for some bit of user data rooted under data-root."
  [user-id & paths]
  (apply fs/file *data-root* (str user-id) (map name paths)))

(defn write-item
  "Write an item to disk, encoded as JSON. Use the contents of the item's :id
  field as its file name."
  [user-id kind item]
  (let [filename (str (:id item) ".json")
        path (get-user-path user-id kind filename)]
    (json/encode-stream item (clojure.java.io/writer path))))

(defn read-item
  "Read an item from disk and decode it from JSON."
  [user-id kind item-id]
  (let [filename (str item-id ".json")
        path (get-user-path user-id kind filename)]
    (json/decode-stream (clojure.java.io/reader path))))

(defn get-access-token-path
  [user-id]
  (get-user-path user-id "access-token.json"))

(defn read-access-token
  [user-id]
  (let [path (get-access-token-path user-id)]
    (json/decode-stream (clojure.java.io/reader path))))

(defn write-access-token
  [user-id access-token]
  (let [path (get-access-token-path user-id)]
    (json/encode-stream access-token (clojure.java.io/writer path))))

(defn make-user-dirs
  "Create the expected directory structure for a user account. Returns true if
  none of the user directories already existed, false otherwise."
  [user-id]
  (let [dirs (map (partial get-user-path user-id) *kinds*)]
    (every? true? (doall (map fs/mkdirs dirs)))))

(defn add-user
  "Add a Twitter user to the directory tree. Returns a boolean indicating
  whether the account was created on disk (ie, whether the expected directory
  structure already existed).

  If the user already exists, the directories won't be created but the
  existing access token will be overwritten by the given access token."
  [user-id access-token]
  (let [created? (make-user-dirs user-id)]
    (write-access-token user-id access-token)
    created?))

(defn user-exists?
  "A user 'exists' if we have an access token file for them."
  [user-id]
  (fs/file? (get-access-token-path user-id)))


require 'digest'
require 'optparse'
# Create a hash sha1 checksum from a file
def checksum(file_path, hash_class)
  # Size of each chunk
  chunk_size = 2048
  # Hash that is the checksum
  hash = hash_class.new
  # File handler
  file_object = File.open(file_path, 'r')
  # loop to update the hash
  while true
    content = file_object.read chunk_size
    # Break the loop if we don't get any byte
    unless content
      return hash.hexdigest
    end
    # Update the hash
    hash.update content
  end
end
# Write the results to database
def write_to_db(hash_db, content)
  file = File.open(hash_db, 'w')
  file.write content
  file.close
end
# get all hashes checksum from the content of a folder
def recursive_get_content(directory_path, hash_class)
  # content buffer
  content = ""
  # Object to hand the directory
  directory_object = Dir.open directory_path
  base_path = File.expand_path directory_path
  # Process all files in directory
  directory_object.each_child do |child|
    # Child to be processed
    child_path = File.join base_path, child
    # When is a directory go recursive
    if File.directory? child_path
      content += "#{recursive_get_content child_path, hash_class}"
    else
      # When it is aa file
      content += "#{child_path},#{checksum child_path, hash_class}\n"
    end
  end
  content
end
# Function to get checksum of input
# noinspection RubyResolve,RubyResolve,RubyResolve,RubyStringKeysInHashInspection
def checksum_handler(file_path, hash_db, hash_function)
  # Reference for hash functions
  hash_functions = {"md5" => Digest::MD5, "sha1" => Digest::SHA1, "sha2" => Digest::SHA2}
  # Get the checksum[s]
  # Check if is a file
  if File.file? file_path
    # Get the hash of the file
    content = "#{File.expand_path(file_path)},#{checksum(file_path, hash_functions[hash_function])}"
  elsif File.directory? file_path
    content = recursive_get_content file_path, hash_functions[hash_function]
  else
    puts 'The file provided exists?'
    return
  end
  content = "#{hash_function}\n#{content}"
  # If a output file is the input .csv
  if hash_db.is_a? String
    # Write all the checksums to the wanted output
    write_to_db hash_db, content
  else
    puts content
  end
end
# Function to compare the hash provided and the one computed
def compare(file_path, hash_class, hash)
  # Check if the file exists
  ## "file_state" if the result of the compared hash and file
  if File.file? file_path
    # Always try to check file permissions
    begin
      # When the file is not corrupted
      if checksum(file_path, hash_class) == hash
        file_state = "SECURE  ------------  "
      else
        # When the file is corrupted
        file_state = "CORRUPTED  ---------  "
      end
    rescue
      # When we can't access to it
      file_state = "ACCESSIONDENIED  ---  "
    end
  else
    # When we can't find the file with the path provided
    # Usually the file was deleted but also returns it can be moved
    file_state = "NOTEXISTS/MOVED  -  "
  end
  puts "#{file_state}#{file_path}"
end
# Compare the checksums from a db with it's files or a raw hash with the one of a file
def compare_hashes_handler(hash_, file_, hash_class)
  # noinspection RubyStringKeysInHashInspection,RubyResolve
  hash_class_reference = {"md5" => Digest::MD5, "sha1" => Digest::SHA1, "sha2" => Digest::SHA2}
  # Check if hash_ is a raw hash or a csv db
  if File.file? hash_
    # Handler for databse
    file_object = File.open hash_, 'r'
    # All the lines of the db
    lines = file_object.readlines
    # Close the file because we don't need it anymore
    file_object.close
    # Fist line of this file is the configuration line
    hash_class = lines[0].strip

    # Parameters for the setup of the hash_function
    hash_class = hash_class_reference[hash_class]

      #puts hash_class, chunk_size
      lines = lines[1..]
      lines.each do |line|
        file_path, hash  = line.strip.split(',')
        compare file_path, hash_class, hash
    end
  else
    # Get the hash class from the string provided
    hash_class = hash_class_reference[hash_class]
    # Compare the raw hash (hash_) with the file provided
    compare file_,hash_class, hash_
  end
end
# main function to execute it
def main
  # Arguments base to be use for reference
  args = {:hash_function => 'md5',:compare => false, :hash => nil, :file => nil}
  # Options to be parsed
  opt = OptionParser.new
  opt.banner = "Checksum handler"
  opt.on("-c", "--compare", "Set the mode to compare") do
    args[:compare] = true
  end
  opt.on("-H", "--hash raw_hash/file", "Raw hash or csv db with path and hashes to compare with (in compare mode) or to write (in checksum mode)") do |value|
    args[:hash] = value
  end
  opt.on("-f", "--file output_file/reference", "File in checksum mode is for checksum;  in compare mode is to compare with a raw hash") do |value|
    args[:file] = value
  end
  opt.on('-5', "--md5", "Use MD5 algorithm") do
    args[:hash_function] = "md5"
  end
  opt.on('-1', '--sha1', 'Use SHA1 algorithm') do
    args[:hash_function] = 'sha1'
  end
  opt.on('-2', '--sha2', 'Use SHA2 algorithm') do
    args[:hash_function] = 'sha2'
  end
  opt.on('-h', '--help') do
    puts opt
    return
  end.parse!

  # If the mode is set to compare
  if args[:compare]
    compare_hashes_handler args[:hash], args[:file], args[:hash_function]
  else
    checksum_handler args[:file], args[:hash], args[:hash_function]
  end
end

main
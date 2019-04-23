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
# get all hashes checksum from the content of a folder
def recursive_get_content(_path, hash_class, file_object, debugmode)
  # When the file is a directory be recursive
  if File.directory? _path
    # Object to hand the directory
    directory_object = Dir.open _path
    base_path = File.expand_path _path
  # Process all files in directory
    directory_object.each_child do |child|
      # Child to be processed
      child_path = File.join base_path, child

      recursive_get_content child_path, hash_class, file_object, debugmode
    end
  else
      # When it is aa file write directly to file_object or print it
      content = "#{File.expand_path _path},#{checksum _path, hash_class}"
      # Debug mode prints every file hash
      if debugmode
        puts content
      end
      # If the user use -o  to output
      if file_object
        file_object.write "#{content}\n"
      end
  end

end
# Function to get checksum of input
def checksum_handler(file_path, hash_db, hash_class, debugmode)
  # Puts hash class that is really a hash function
  if debugmode
    puts hash_class
  end
  # Write to target if is stablished
  if hash_db.is_a? String
    # Handler for the next writes
    file_object = File.open hash_db, 'w'
    file_object.write "#{hash_class}\n"
  else
    # When not file is set
    file_object = nil
  end
  # Stablish the hash class
  hash_class = {1 => Digest::SHA1, 2 => Digest::SHA2, 5 => Digest::MD5}[hash_class]
  # Recursive mode also works with files
  recursive_get_content file_path, hash_class, file_object, debugmode
  # If we are redirecting the hashes to a file finally close it
  if file_object
    file_object.close
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
  hash_class_reference = {1 => Digest::SHA1, 2 => Digest::SHA2, 5 => Digest::MD5}
  # Check if hash_ is a raw hash or a csv db
  if File.file? hash_
    # Handler for databse
    file_object = File.open hash_, 'r'
    # All the lines of the db
    lines = file_object.readlines
    # Close the file because we don't need it anymore
    file_object.close
    # Fist line of this file is the configuration line
    hash_class = lines[0].strip.to_i

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
  args = {:hash_function => 1,:compare => false, :debugmode => false, :hash => nil, :file => nil, :output_file => nil}
  # Options to be parsed
  opt = OptionParser.new
  opt.banner = "Checksum handler; Usage: checksum.rb <options> FILE"
  opt.on("-c", "--compare HASH/HASHDB", "Set the mode to compare an input hash with the FILE or to compare all hashes of the with all file inside it") do |value|
    args[:compare] = value
  end
  opt.on('-v', '--verbose', 'Verbose mode ON') do
    args[:compare] = true
  end
  opt.on("-o", "--output-file FILENAME", "Output file for the checksum (csv)") do |value|
    args[:output_file] = value
  end
  opt.on('-5', "--md5", "Use MD5 algorithm") do
    args[:hash_function] = 5
  end
  opt.on('-1', '--sha1', 'Use SHA1 algorithm (Set by default)') do
    args[:hash_function] = 1
  end
  opt.on('-2', '--sha2', 'Use SHA2 algorithm') do
    args[:hash_function] = 2
  end
  opt.on('-h', '--help') do
    puts opt
    return
  end.parse!
  # Get the FILE variable
  args[:file] = ARGV.pop
  # If the mode is set to compare

  begin
    if args[:compare]
      compare_hashes_handler args[:compare], args[:file], args[:hash_function]
    else
      checksum_handler args[:file], args[:output_file], args[:hash_function], args[:debugmode]
    end
  rescue => error
    # For debugging
    puts error
    # Print options
    puts opt
  end

end

main
require 'digest'
require 'optparse'

# get the folder base of the target file
# used by samefolder option hat change file path to ./ as the script was working in the same folder
def getfolder(file)
  # Directory to return after analysing the target
  current_dir = Dir.pwd
  # when the target is a directory cd into inmediatly
  if File.directory? file
    Dir.chdir file
    # Get the folder that is going to be replaced with ./
    directory = Dir.pwd + '/'
  else
    # When the target is a file we need to get it's location
    splited_file_path = File.expand_path(file).split('/')
    # this limit reference the last folder before the filename
    limit = splited_file_path.length - 1
    # Get into the same folder of the target file
    Dir.chdir splited_file_path[0...limit].join('/')
    # Get the folder that is going to be replaced with ./
    directory = Dir.pwd + '/'
  end
  # Return to the original working directory
  Dir.chdir current_dir
  # return the founded directory that is going to be repalced in the target's path with './'
  directory
end
# Create a hash sha1 checksum from a file
def checksum(file_path, hash_class, _bit_size)
  # Size of each chunk
  chunk_size = 2048
  # Hash that is the checksum function
  # when a bitsize was specified
  if _bit_size
    hash = hash_class.new(_bit_size)
  else
    hash = hash_class.new
  end
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
def recursive_checksum(_path, hash_class, _bit_size, file_object, debugmode, samefolder)
  begin
    # When the file is a directory be recursive
    if File.directory? _path
      # Object to hand the directory
      directory_object = Dir.open _path
      base_path = File.expand_path _path
    # Process all files in directory
      directory_object.each_child do |child|
        # Child to be processed
        child_path = File.join base_path, child

        recursive_checksum child_path, hash_class, _bit_size,file_object, debugmode, samefolder
      end
    else
      # path to be used
      if samefolder
        # use ./ for base example ./filename.txt
        file_path = _path.sub(samefolder, './')
      else
        # use complete path to file
        file_path = File.expand_path _path
      end
      # When it is aa file write directly to file_object or print it
      content = "#{file_path},#{checksum _path, hash_class, _bit_size}"
      # Debug mode prints every file hash
      if debugmode
        puts content
      end
      # If the user use -o  to output
      if file_object
        file_object.write "#{content}\n"
      end
    end
  rescue
    nil
  end

end
# Function to get checksum of input
def checksum_handler(file_path, hash_db, hash_class, _bit_size, debugmode, samefolder)
  # Reference for hash banner  to notice wat function is using
  reference_banner = {1 => "SHA1", 2 => "SHA2-#{_bit_size}", 5 => "MD5"}[hash_class]
  # returns path as the script was in the same folder
  if samefolder
    samefolder = getfolder file_path
  end
  # Puts hash class that is really a hash function that is going to be used
  if debugmode
    puts reference_banner
  end
  # Write to target if is stablished
  if hash_db.is_a? String
    # Handler for the next writes
    file_object = File.open hash_db, 'w'
    # Write the banner; useful for compare mode
    file_object.write "#{reference_banner}\n"
  else
    # When not file is set
    file_object = nil
  end
  # Stablish the hash class
  hash_class = {1 => Digest::SHA1, 2 => Digest::SHA2, 5 => Digest::MD5}[hash_class]
  # Recursive mode also works with files
  recursive_checksum file_path, hash_class, _bit_size, file_object, debugmode, samefolder
  # If we are redirecting the hashes to a file finally close it
  if file_object
    file_object.close
  end
end
# Function to compare the hash provided and the one computed
def compare(file_path, hash_class, _bit_size, hash)
  # Check if the file exists
  ## "file_state" if the result of the compared hash and file
  if File.file? file_path
    # Always try to check file permissions
    begin
      # When the file is not corrupted
      if checksum(file_path, hash_class, _bit_size) == hash
        file_state = "SECURE  ------------  "
      else
        # When the file is corrupted
        file_state = "CORRUPTED  ---------  "
      end
    rescue => error
      puts error
      # When we can't access to it
      file_state = "ACCESSDENIED  ---  "
    end
  else
    # When we can't find the file with the path provided
    # Usually the file was deleted but also returns it can be moved
    file_state = "NOTEXISTS/MOVED  -  "
  end
  puts "#{file_state}#{file_path}"
end
# Compare the checksums from a db with it's files or a raw hash with the one of a file
def compare_hashes_handler(hash_, file_, hash_class, _bit_size)
  # noinspection RubyStringKeysInHashInspection,RubyResolve
  hash_class_reference = {1 => Digest::SHA1, 2 => Digest::SHA2, 5 => Digest::MD5}
  # Check if hash_ is a raw hash or a csv db
  if File.file? hash_
    # hash_ is a csv database with hashes to check
    # Handler for databse
    file_object = File.open hash_, 'r'
    # All the lines of the db
    lines = file_object.readlines
    # Close the file because we don't need it anymore
    file_object.close
    # Fist line of this file is the configuration line that is the function and its bit size (if is sha2)
    hash_class, _bit_size = lines[0].strip.split('-')
    # Has_class can be transformed to int corresponding to its number
    hash_class = {"SHA1" => 1, "SHA2" => 2, "MD5" => 5}[hash_class]
    # When a bit size was specified transform it to int
    if _bit_size.is_a? String
      _bit_size = _bit_size.to_i
    end
    # Parameters for the setup of the hash_function
    hash_class = hash_class_reference[hash_class]

      #puts hash_class, chunk_size
      lines = lines[1..]
      lines.each do |line|
        file_path, hash  = line.strip.split(',')
        compare file_path, hash_class, _bit_size, hash
    end
  else
    # hash_ variable is a raw hash
    # Get the hash class from the string provided
    hash_class = hash_class_reference[hash_class]
    # Compare the raw hash (hash_) with the file provided
    compare file_,hash_class, _bit_size, hash_
  end
end
# main function to execute it
def main
  # Arguments base to be use for reference
  args = {:hash_function => 1,:compare => false, :debugmode => false, :samefolder => false, :hash => nil, :file => nil, :output_file => nil}
  # Options to be parsed
  opt = OptionParser.new
  opt.banner = "Checksum handler; Usage: checksum.rb <options> FILE"
  opt.on("-c", "--compare HASH/HASHDB", "Set the mode to compare an input hash with the FILE or to compare all hashes of the with all file inside it") do |value|
    args[:compare] = value
  end
  opt.on('-v', '--verbose', 'Verbose mode ON') do
    args[:debugmode] = true
  end
  opt.on('-s', '--same-folder', 'Change the target file path to ./ as this script was working in the same folder; useful shareable files') do
    args[:samefolder] = true
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
  opt.on('-2', '--sha2 BITSLENGTH', 'Use SHA2 algorithm with your specific bit lenth can be 256, 384 or 512') do |bit_size|
    # SHA2 can have different bit sizes like 224, 256, 384, 512
    if [256, 384, 512].find bit_size.to_i
      args[:bit_size] = bit_size.to_i
    end
    args[:hash_function] = 2
  end
  opt.on('-h', '--help') do
    puts opt
    return
  end.parse!
  # Get the FILE variable
  args[:file] = ARGV.pop
  # When no target is specified
  unless args[:file]
    # iif compare mode isn't enabled
    unless args[:compare]
      puts opt
    end

  end
  begin
    # If the mode is set to compare
    if args[:compare]
      compare_hashes_handler args[:compare], args[:file], args[:hash_function], args[:bit_size]
    else
      # Get check sum from file
      checksum_handler args[:file], args[:output_file], args[:hash_function], args[:bit_size],args[:debugmode], args[:samefolder]
    end
  rescue => error
    # For debugging
    puts error
    # Print options
    puts opt
  end
end
main